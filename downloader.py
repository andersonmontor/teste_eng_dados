# Este arquivo é responsável por baixar as páginas e salvar num banco de dados 

import threading
import os
import time
from DAOs import PaginasDAO
from datetime import datetime
from urllib.request import Request, urlopen

# Como as chamadas vão ser bloqueadoras por IO,
# nao precisam ser limitadas por numero de cores de CPU
# (até porque python nem faz uso de mais de 1)
# O numero ideal seria o maximo que o servidor deixa de limite de requisicões
N_THREADS = 20
TIPOS_LINK = "mercadolivre.com.br/p", "produto.mercadolivre.com.br", "magazineluiza.com.br", "casasbahia.com.br"
PASTA_BAIXADOS = "paginas_baixadas"

f = open("./rawdata/offers.csv")
links = f.read().split('\n')
f.close()

print ("Contando quantos links ja existem no banco de paginas...")
DAOinicial = PaginasDAO()
links_ja_baixados = DAOinicial.todos_links()
print ("Paginas baixadas: %d tuplas." % len(links_ja_baixados))

# Mutexes pra sincronização de threads
lock = threading.Lock()
bd_lock = threading.Lock()

# Retorna qual tipo de um link
def _qual_tipo(link):
	for tipo in TIPOS_LINK:
		if tipo in link:
			return tipo


# Separa links pelos tipos
def separa_links(links):
	dict_links = {}
	for tipo in TIPOS_LINK:
		dict_links[tipo] = []
		
	for link in links:
		tipo = _qual_tipo(link)
		dict_links[tipo].append(link)
				
	return dict_links
	
	
def baixa_pagina(link):
	dados = None
	tentativas = 0
	while tentativas < 5:
		try:
			req = Request(link, headers={'User-Agent': 'Mozilla/5.0'})
			dados = urlopen(req).read()
			break
		except Exception as exc:
			print ("ERRO, tentando novamente:", link, )
			print (exc)
			tentativas += 1
			
	return dados
	
				
# Funcao a ser executada por cada thread, baixa pagina e salva na pasta correspondente
def trabalho_thread():
	
	# Objeto que se conecta ao banco de dados
	p_DAO = PaginasDAO()
	
	# Mutex, apenas uma unica thread pode estar executando essa linha de codigo ao mesmo tempo
	while True:
		with lock:
			if len(links) <= 0:
				p_DAO.fechar()
				return
			link = links.pop()
			
		if link in links_ja_baixados:
			print ("JÁ BAIXADO ANTES: %s" % link)
			continue # Ja foi baixado antes, vai pro proximo
			
		if "casasbahia.com.br" in link:
			continue # Está dando erro [Errno socket error] [WinError 10053], não consegui resolver ainda
		
		dados = baixa_pagina(link)
		with lock:
			restante = len(links)
			
		if dados:
			print ("OK(%d restantes): %s" % (restante, link))
		else:
			print ("ERRO, nao foi possivel baixar:", link)
			continue
		
		
		with bd_lock:
			p_DAO.inserir(link, str(dados))
			
			
def baixa_todas():	
	
	n = len(links)
	pergunta = "CSV contém %d links, caso deseje reduzir para um número menor, digite o número, caso contrário, apenas aperte ENTER: " % n
	to_remove = input(pergunta).strip()
	if to_remove.isdigit():
		for i in range(n - int(to_remove)):
			links.pop()

	# Inicializacao do banco de dados
	DAOinicial = PaginasDAO()
	
	# Conta e mostra quanto tem de cada link
	dict_links = separa_links(links)
	print ("Quantidade de links encontrados:", len(links))
	for tipo in TIPOS_LINK:
		print ("%s: %d" % (tipo, len(dict_links[tipo])))
		
	# Cria pasta geral de paginas baixadas
	if not os.path.isdir(PASTA_BAIXADOS):
		os.mkdir(PASTA_BAIXADOS)
		
	# Cria subpastas pra cada tipo de link
	for tipo in TIPOS_LINK:
		tipo_r = tipo.replace('/', '(barra)') # Sistema de arquivos nao deixa salvar com '/'
		caminho = "./%s/%s" % (PASTA_BAIXADOS, tipo_r)
		if not os.path.isdir(caminho):
			os.mkdir(caminho)
			
	# Cria threads pra baixar paginas
	for i in range(N_THREADS):
		thread = threading.Thread(target = trabalho_thread)
		thread.setDaemon(True) # Pra parar no Ctrl+C
		thread.start()
		
	# Espera todas threads terminar
	comeco = datetime.now()
	while threading.active_count() > 1:
		time.sleep(0.1)
		
	DAOinicial.fechar()
		
	print ("Paginas baixadas, tempo de execução:", (datetime.now() - comeco))
	
if __name__ == "__main__":
	baixa_todas()