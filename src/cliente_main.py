from segmentoTCP import*
from cliente_TCP_LIB import*
from socket import*
import sys
import random
import threading
import time
import pickle
		
def main():
	global timer_running
	
	SEG_SIZE = 1024 #tamanho máximo do segmento
	
	#definindo servidor
	server_name = "localhost"
	server_port = 12000
	server_addr = (server_name, server_port)

	#criando socket UDP
	cliente = socket(AF_INET, SOCK_DGRAM)
	cliente.bind(("localhost", 10000)) #definindo porta do socket cliente
	
	#buffer que contém os dados a serem enviados
	MAX_SIZE = 200
	buffer = []
	
	#declarando janela de transmissão e outras variaveis de controle
	next_seqnum = random.randint(0, 100) #seq_num inicial aleatorio
	last_sent = last_acked = -1
	NUM_PACOTES = 10 #numero de pacotes a serem enviados
	SEQNUM_FINAL = next_seqnum + NUM_PACOTES - 1
	send_base = [next_seqnum]
	rwnd = 0 	  #número máximo de bytes não reconhecidos na rede (janela de transferencia)
	ack = -1	  #numero de reconhecimento recebido do servidor
	ack_aux = -1  #auxiliares para contar acks repetidos
	ack_count = 0
	
	#criando timer
	timer = [0]
	timer[0] = threading.Timer(5, function = timeout, args = (cliente, buffer, send_base, server_addr, timer))
	
	
	print("CLIENTE INICIADO...\n\nSeqNum Inicial: ", next_seqnum)
	print("\n\nINICIANDO RECONHECIMENTO DE TRÊS VIAS...")
	print("\n\n---------------------------------------------------------------------------\n\n")
	time.sleep(3)
	
	start_time = time.process_time() #para calcular o tempo total de transferência
	
	#3-way handshake
	
	#	1.Envia SYN
	
	print("ENVIANDO SYN...\n")
	
	get_data(buffer, MAX_SIZE, next_seqnum-1, None, True) 
	enviar_pacote(cliente, buffer, next_seqnum, server_addr, timer, send_base)
	timer_running = True
	last_sent = next_seqnum
	next_seqnum += 1
	
	time.sleep(2)
	
	#	2.Recebe SYNACK
	
	print("\nRECEBENDO SYNACK...\n")
	ack, server_addr = cliente.recvfrom(SEG_SIZE)
	ack = pickle.loads(ack)
	
	while not (ack.syn and ack.ack):
		ack, server_addr = cliente.recvfrom(SEG_SIZE)
		ack = pickle.loads(ack)
	
	rwnd = ack.rwnd #ajusta janela de transferencia
	ack = ack.ack_num #pega valor do número de reconhecimento
	update_buffer(buffer, ack)
	last_acked = ack - 1
	send_base[0] = last_acked + 1
	timer[0].cancel()
	timer_running = False
	
	print("Recebido - Ack: ", ack, "\n")
	print("rwnd: ", rwnd, "\n\n")
	
	time.sleep(3)
	
	#	3.Envia ACK
	
	print("ENVIANDO ACK...\n")
	get_data(buffer, MAX_SIZE, last_sent, None, ack = True) 
	enviar_pacote(cliente, buffer, next_seqnum, server_addr, timer, send_base)
	timer_running = True
	last_sent += 1
	next_seqnum += 1
	
	cliente.setblocking(0)
	
	time.sleep(2)
	
	#iniciando transferência de dados
	while last_acked < SEQNUM_FINAL:
	
		get_data(buffer, MAX_SIZE, last_sent, random.randint(1, 100)) #simula recebimento de dados da aplicação
		
		#verifica janela de transferencia
		if (next_seqnum <= SEQNUM_FINAL) and (last_sent - last_acked < rwnd):
			enviar_pacote(cliente, buffer, next_seqnum, server_addr, timer, send_base)
			timer_running = True
			last_sent += 1
			next_seqnum += 1
		else:
			if(last_sent - last_acked >= rwnd):
				print("NÚMERO DE PACOTES NÃO RECONHECIDOS NA ")
				print("REDE(", last_sent-last_acked,") >= rwnd (", rwnd, ") ==> Enviar pacote de teste\n")
			else:
				print("NÃO HÁ MAIS PACOTES A ENVIAR ==> Enviar pacote de teste")
			get_data(buffer, MAX_SIZE, -2, None, ack = True) 
			enviar_pacote(cliente, buffer, -1, server_addr, timer, send_base, True)
			
		#recebe mensagens do servidor
		try:
			ack, server_addr = cliente.recvfrom(SEG_SIZE)
			ack = pickle.loads(ack)
			rwnd = ack.rwnd #ajusta janela de transferencia
			ack = ack.ack_num #pega valor do número de reconhecimento
			
			update_buffer(buffer, ack)
			
			last_acked = ack - 1
			send_base[0] = last_acked + 1
			print("Recebido - Ack: ", ack, "\n")
			print("rwnd: ", rwnd, "\n\n")
			
			#se houver pacotes não reconhecidos, reinicia timer
			if last_sent > last_acked:
				timer[0].cancel()
				timer_running = False
				start_timer(cliente, buffer, send_base, server_addr, timer)

			#Verifica acks repetidos e reenvia pacote se necessário
			if (ack == ack_aux):
				ack_count += 1
				if (ack_count == 3): #três acks duplicados, reenvia pacote
					print("TRÊS ACKs DUPLICADOS! - Ack: ", ack_aux, "\n")
					enviar_pacote(cliente, buffer, ack_aux, server_addr, timer, send_base)
					ack_count = 0
			else:
				ack_aux = ack
				ack_count = 1
				
		except Exception as e:
			pass
	
	end_time = time.process_time()
	tempo_total = end_time-start_time
	print("\n\nTodos os pacotes enviados e reconhecidos.\n")
	print("\nESTATÍSTICAS\n")
	print("\nTempo Total de Transferência = ", tempo_total, " segundos.\n")
	print("Atraso Médio dos Pacotes = ", tempo_total/(2*NUM_PACOTES), " segundos.\n\n")
	
if __name__ == "__main__":
	main()
