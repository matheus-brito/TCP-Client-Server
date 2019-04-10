from segmentoTCP import*
from socket import*
import time
import random
import pickle
import sys

def perder_Pacote():
	chance = 35 #chance de perder pacote em porcentagem
	aux = random.randint(1, 100)
	if(aux <= chance):
		return True
	else:
		return False	

#Exibe elementos ainda não lidos pela aplicação
def print_buffer(buffer):
	
	print("\nBUFFER (elementos não lidos):\n")
	if len(buffer) == 0:
		print("\n    Vazio")
	else:
		for i in range(0, len(buffer)):
			print("\n    ", i, "- SeqNum: ", buffer[i].seq_num)
	print("\n")
	
def enviar_ack(seq_num, rec_num, server, cliente_addr, rwnd, syn = False):
	segTCP = SegmentoTCP(syn = syn, ack = True, ack_num = rec_num, rwnd = rwnd) 
	if not perder_Pacote():
		print("Enviado - RecNum: ", rec_num, "\n")
		print("rwnd: ", rwnd, "\n\n")
		server.sendto(pickle.dumps(segTCP), cliente_addr)
	else:
		print("Pacote Perdido - RecNum: ", rec_num, "\n")
		print("rwnd: ", rwnd, "\n\n")
	
#Armazena msg se não foi recebida. Simula envio de dados para a camada de aplicação
def processar_msg(buffer, msg, pckt_read, pckt_rcv, size, rwnd, last_read):
	

	aux = next((x for x in buffer if x.seq_num == msg.seq_num), None)
	if len(buffer) < size and aux == None and msg.seq_num > last_read[0]:
		if len(buffer) == 0:
			buffer.append(msg)
		else:
			inserido = False
			for i in range(0, len(buffer)):
				if msg.seq_num < buffer[i].seq_num:
					buffer.insert(i, msg)
					inserido = True
					break
			if not inserido:
				buffer.append(msg)

		pckt_rcv[0] += 1
		
	#retira pacotes com seq_num sequenciais
	if len(buffer) > 1 and buffer[0].seq_num == last_read[0]+1:
		aux = buffer[0].seq_num
		existem_sequenciais = False
		for i in range(1, len(buffer)):
			if buffer[i].seq_num == aux + 1:
				aux = buffer[i].seq_num
				last_read[0] = buffer[i].seq_num
				pckt_read[0] += 1
				existem_sequenciais = True
			else:
				break
		
		if existem_sequenciais:
			pckt_read[0] += 1  #para que o valor de dados lidos seja correto
			buffer = [x for x in buffer if x.seq_num > last_read[0]]
	
	rwnd[0] = size - (pckt_rcv[0] - pckt_read[0])
	
	return buffer
