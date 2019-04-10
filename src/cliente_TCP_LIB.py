from segmentoTCP import*
from socket import*
import sys
import random
import threading
import time
import pickle

timer_running = False

#remove segmentos reconhecidos do buffer
def update_buffer(buffer, ack):
	aux = 0
	for i in range(0, len(buffer)):
		if buffer[i].seq_num >= ack:
			break
		else:
			aux += 1
	
	for i in range(0, aux):
		buffer.pop(0)

def start_timer(cliente, buffer, send_base, server_addr, timer):
	global timer_running

	if not timer_running:
		timer[0] = threading.Timer(5, function = timeout, args = (cliente, buffer, send_base, server_addr, timer))
		timer[0].start()
		timer_running = True
		print("Timer Iniciado\n")

#simula a criação de segmentos TCP e adiciona ao buffer de envio
def get_data(buffer, size, last_sent, dados, syn = False, ack = False):
	if(len(buffer) < size):
		segTCP = SegmentoTCP(syn, ack, seq_num = last_sent + 1, dados = dados) 
		buffer.append(segTCP)

#envia pacotes e inicia o timer
def enviar_pacote(cliente, buffer, seq_num, server_addr, timer, send_base, teste = False):
	
	segTCP = [x for x in buffer if x.seq_num == seq_num]
	
	if not perder_Pacote():
		cliente.sendto(pickle.dumps(segTCP[0]), server_addr)
		print("Enviado - SeqNum: ", seq_num, "\n")
	else:
		print("Pacote Perdido - SeqNum: ", seq_num, "\n")
	
	if not teste:
		start_timer(cliente, buffer, send_base, server_addr, timer)
		
	print("\n\n---------------------------------------------------------------------------\n\n")
	time.sleep(2) #Pausar Execução para visualizar as informações

	#Reenvia pacote em caso de timeout		
def timeout(cliente, buffer, send_base, server_addr, timer):
	global timer_running
	
	print("TIMEOUT! - SendBase: ", send_base[0], "\n")
	timer_running = False
	enviar_pacote(cliente, buffer, send_base[0], server_addr, timer,send_base)

#Decide se o pacote será perdido ou não		
def perder_Pacote():
	chance = 20 #chance de perder pacote em porcentagem
	aux = random.randint(1, 100)
	if(aux <= chance):
		return True
	else:
		return False