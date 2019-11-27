# Este arquivo tem como objetivo fazer a extração dos dados relevantes contidos nas paginas dos links fornecidos

import requests
from bs4 import BeautifulSoup as bs
from DAOs import PaginasDAO, ExtraidosDAO


# Link da pagina -> tupla de dados
# Preço é representado em centavos, ou seja, R$ 100 -> 10000; R$ 100,50 -> 10050; etc
def extrai_dados(link, conteudo_html):
	soup = bs(conteudo_html, "html.parser")
	tupla = None
	
	if "produto.mercadolivre.com.br" in link.lower():
		tupla = _mercado_livre(soup, 1)
	elif "mercadolivre.com.br/p" in link.lower():
		tupla = _mercado_livre(soup, 2)
	elif "magazineluiza.com.br" in link.lower():
		tupla = _magazine(soup)
	else:
		print("Ainda não implementado.")
		
	output = [link] + list(tupla)
	return output
	
def _mercado_livre(soup, tipo):
	if tipo == 1:
		titulo = soup.find(class_ = "item-title").find(class_ = "item-title__primary")
	elif tipo == 2:
		titulo = soup.find(class_ = "ui-pdp-title")
		
	assert(titulo)
	titulo_parsed = titulo.get_text().strip()
	
	if not soup.find("div", class_ = "ui-pdp-warning-message"):
		tag_preco = soup.find(class_ = "price-tag")
		preco_inteiro = tag_preco.find(class_ = "price-tag-fraction")
		preco_centavos = tag_preco.find(class_ = "price-tag-cents")
		assert(preco_inteiro)
		if preco_centavos:
			assert(preco_centavos.get_text().isdigit())
			
		p_inteiro_parsed = preco_inteiro.get_text().replace('.', '')
		
		if preco_centavos:
			preco = int(p_inteiro_parsed) * 100 + int(preco_centavos.get_text())
		else:
			preco = int(p_inteiro_parsed) * 100
	else:
		erro = soup.find("div", class_ = "ui-pdp-warning-message").find("h3")
		if erro and ("sem estoque" in erro.get_text().strip().lower()):
			preco = "SEM_ESTOQUE"
		else:
			preco = None
		
	tupla = (titulo_parsed, preco)
		
	return tupla
	
def _magazine(soup):
	tenta_titulo = soup.find(class_ = "header-product__title")
	preco = None
	if tenta_titulo:
		titulo = tenta_titulo.get_text().strip()
	elif soup.find(class_ = "header-product__title--unavailable"):
		titulo = soup.find(class_ = "header-product__title--unavailable").get_text().strip()
		return (titulo, "SEM_ESTOQUE")
	
	tenta_preco = soup.find(class_ = "price-template__text")
	if tenta_preco:
		preco = tenta_preco.get_text().strip().replace('.', '').replace(',', '')
		preco = int(preco)
	
	
	return (titulo, preco)
		
# Extrai dados de todas as paginas e guarda no banco de dados
def extrai_todos():
	paginasDAO = PaginasDAO()	
	dadosDAO = ExtraidosDAO()
	
	print ("Obtendo links do banco de páginas...")
	links = paginasDAO.todos_links()
	links_ja_extraidos = dadosDAO.todos_links()
	
	i = 0
	for link in links:
		if link not in links_ja_extraidos:
			html = paginasDAO.consultar(link)
			tupla = extrai_dados(link, html)
			preco = tupla[2]
			if not isinstance(preco, int):
				preco = -1
			
			dadosDAO.inserir(link, tupla[1], preco)
			i += 1
			print ("(%s/%s) %s" % (i, len(links), link))
		else:
			print ("JA ANALISADO ANTES:", link)			
			
	paginasDAO.fechar()
	dadosDAO.fechar()
		
	
if __name__ == "__main__":
	extrai_todos()
	
	