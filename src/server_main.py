from segmentoTCP import*
from server_TCP_LIB import*
from socket import*
import time
import random
import pickle
import sys

def main():
	#criando server
	server_port = 12000
	server = socket(AF_INET, SOCK_DGRAM)
	server.bind(("localhost", server_port))
	
	#declarando variaveis de controle
	MAX_SIZE = 10 #tamanho máximo buffer
	rwnd = [MAX_SIZE] #janela de transferencia inicial é igual ao tamanho do buffer
	buffer = [] #buffer de recebimento
	rec_num = 0
	last_read = [-1] #número de sequencia do ultimo pacote lido do buffer
	pckt_read = [0] #numero pacotes "lidos" pela aplicação
	pckt_rcv = [0]  #numero pacotes recebidos pelo socket
	seq_num = random.randint(0,100) #numero de sequencia aleatorio
	SEG_SIZE = 1024 #tamanho máximo do segmento
	
	print("SERVIDOR DISPONÍVEL...\n\nSeqNum Inicial: ", seq_num, "\n")
	print("Janela de Transferência (rwnd) Inicial: ", rwnd[0], " pacotes")
	print("\n\nAGUARDANDO RECONHECIMENTO DE TRÊS VIAS...")
	print("\n\n---------------------------------------------------------------------------\n\n")
	time.sleep(3)
	
	#3-way handshake
	
	#	1 - Recebe SYN
	
	msg, cliente_addr = server.recvfrom(SEG_SIZE)
	msg = pickle.loads(msg)
	
	while not msg.syn:
		msg, cliente_addr = server.recvfrom(SEG_SIZE)
		msg = pickle.loads(msg)

	rec_num = msg.seq_num + 1
	last_read[0] = msg.seq_num - 1 #inicializando last_read
	buffer = processar_msg(buffer, msg, pckt_read, pckt_rcv, MAX_SIZE, rwnd, last_read)
	
	print("RECEBENDO SYN...\n\n")
	print("Recebido - SeqNum: ", msg.seq_num, "\n")
	
	print_buffer(buffer)
	
	print("\n\n---------------------------------------------------------------------------\n\n")
	time.sleep(3)
	
	#	2 - Enviar SYNACK
	
	print("ENVIANDO SYNACK...\n\n")
	rec_num_SYNACK = rec_num #variavel auxiliar
	enviar_ack(seq_num, rec_num, server, cliente_addr, rwnd[0], True)
	seq_num += 1
	
	time.sleep(2)
	
	#	3 - Receber ACK (A lógica é a mesma de se receber qualquer pacote,
	#   portanto o código abaixo se aplica a essa situação.)
	
	print("RECEBENDO ACK...\n\n")
	
	#Recebe pacotes, processa e envia ACKs
	while True:
		msg, cliente_addr = server.recvfrom(SEG_SIZE)
		msg = pickle.loads(msg)
		buffer = processar_msg(buffer, msg, pckt_read, pckt_rcv, MAX_SIZE, rwnd, last_read)
		
		print("Recebido - SeqNum: ", msg.seq_num, "\n")
		
		print_buffer(buffer)
		
		if(last_read[0] > rec_num):
			rec_num = last_read[0]+1
		elif(msg.seq_num == rec_num):
			rec_num += 1
		
		#caso seja necessario reeviar o SYNACK devido perda
		if(rec_num == rec_num_SYNACK):
			enviar_ack(seq_num, rec_num, server, cliente_addr, rwnd[0], True)
		else:
			enviar_ack(seq_num, rec_num, server, cliente_addr, rwnd[0])
			
		seq_num += 1
		
		print("\n\n---------------------------------------------------------------------------\n\n")
		
if __name__ == "__main__":
	main()
