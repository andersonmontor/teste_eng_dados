# Aqui serÃ£o encapsuladas os acessos ao banco de dados local(sqlite3)
# Detalhe: por ser um teste, o esquema do BD n?o está normalizado

import sqlite3
import os

TIPOS_LINK = "mercadolivre.com.br/p", "produto.mercadolivre.com.br", "magazineluiza.com.br", "casasbahia.com.br"

def _qual_tipo(link):
	for tipo in TIPOS_LINK:
		if tipo in link:
			return tipo


# Guarda conteudo HTML das paginas
class PaginasDAO:
	
	def __init__(self, nomebd = "paginas.db"):
		self.nomebd = nomebd
		self.conn = None
		if not os.path.isfile(nomebd):
			self.cria_bd()		
		self._conecta_bd()
	
	def _conecta_bd(self):
		if not self.conn:
			try:
				self.conn = sqlite3.connect(self.nomebd)
			except Exception as e:
				print (e)
	
	def cria_bd(self):
		self._conecta_bd()
		cur = self.conn.cursor()				
		cur.execute("CREATE TABLE paginas (link text, tipo text, HTML text)")
		cur.execute("CREATE INDEX link_indice ON paginas (link)")
		self.conn.commit()

	def inserir(self, link, html):
		cur = self.conn.cursor()	
		tipo = _qual_tipo(link)
		cur.execute("INSERT INTO paginas VALUES (?,?,?)", (link, tipo, html))
		self.conn.commit()

	def consultar(self, link):
		cur = self.conn.cursor()	
		cur.execute("SELECT HTML FROM paginas WHERE link=?", (link,))
		return cur.fetchall()[0][0]
		
	def todos_links(self):
		cur = self.conn.cursor()
		cur.execute("SELECT link FROM paginas")	
		links = cur.fetchall()	
		output = []
		for l in links:
			output.append(l[0])
		
		return output
		
	def existe_link(self, link):
		cur = self.conn.cursor()	
		cur.execute("SELECT * FROM paginas WHERE link=?", (link,))
		return len(cur.fetchall()) > 0
		
	def fechar(self):
		if self.conn:
			self.conn.close()
		self.conn = None
	
# Guarda dados extraidos
class ExtraidosDAO:
	def __init__(self, nomebd = "extraidos.db"):
		self.nomebd = nomebd
		self.conn = None
		if not os.path.isfile(nomebd):
			self.cria_bd()		
		self._conecta_bd()
	
	def _conecta_bd(self):
		if not self.conn:
			try:
				self.conn = sqlite3.connect(self.nomebd)
			except Exception as e:
				print (e)
				
	def cria_bd(self):
		self._conecta_bd()
		cur = self.conn.cursor()				
		cur.execute("CREATE TABLE dados_extraidos (link text, tipo text, titulo_prod text, preco_prod integer)")
		cur.execute("CREATE INDEX link_indice ON dados_extraidos (link)")
		self.conn.commit()
		
	def inserir(self, link, titulo, preco):
		cur = self.conn.cursor()		
		tipo = _qual_tipo(link)
		cur.execute("INSERT INTO dados_extraidos VALUES (?,?,?,?)", (link, tipo, titulo, preco))
		self.conn.commit()
		
	def consultar(self, link):
		cur = self.conn.cursor()	
		cur.execute("SELECT * FROM dados_extraidos WHERE link=?", (link,))
			
		return cur.fetchall()[0]

	def existe_link(self, link):
		cur = self.conn.cursor()	
		cur.execute("SELECT * FROM dados_extraidos WHERE link=?", (link,))
		return len(cur.fetchall()) > 0
		
	def todos_links(self):
		cur = self.conn.cursor()
		cur.execute("SELECT link FROM dados_extraidos")	
		links = cur.fetchall()	
		output = []
		for l in links:
			output.append(l[0])
		
		return output

	def todos_dados(self):
		cur = self.conn.cursor()
		cur.execute("SELECT link, titulo_prod, preco_prod FROM dados_extraidos")			
		return cur.fetchall()
		
	def fechar(self):
		if self.conn:
			self.conn.close()
		self.conn = None