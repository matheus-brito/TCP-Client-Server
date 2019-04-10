#Simula um segmento TCP simplificado

class SegmentoTCP:
	def __init__(self, syn, ack, seq_num = None, ack_num = None, dados = None, rwnd = None):
		self.syn = syn
		self.ack = ack
		self.seq_num = seq_num
		self.dados = dados
		self.ack_num = ack_num
		self.rwnd = rwnd