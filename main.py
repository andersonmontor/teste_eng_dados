# Conciliação dos códigos, menuzinho simples pro usuário escolher o que quer fazer

import downloader
import extracao
from DAOs import PaginasDAO, ExtraidosDAO

opcoes = """1 - Baixar paginas
2 - Extrair dados das paginas baixadas
3 - Consultar dados de um link especifico
4 - Sair
"""

paginasDAO = PaginasDAO()
dadosDAO = ExtraidosDAO()

print ("Contando quantos links ja existem no banco de dados já extraidos...")
links_ja_analisados = dadosDAO.todos_links()
n = len(links_ja_analisados)

print ("Extraidos: %d tuplas.\n" % n)

while True:
	print (opcoes)
	escolha = input(">> ")

	if escolha == '1':
		downloader.baixa_todas()
	elif escolha == '2':
		extracao.extrai_todos()
		links_ja_analisados = dadosDAO.todos_links()
	elif escolha == '3':
		escolha_link = input("Link: ").strip()
		if escolha_link in links_ja_analisados:
			print ("Link encontrado no banco de dados extraídos!")
			tupla = dadosDAO.consultar(escolha_link)
		else:
			print ("Link não encontrado no banco, baixando página...")
			pagina = downloader.baixa_pagina(escolha_link)
			tupla = extracao.extrai_dados(escolha_link, pagina)
		
		preco = tupla[3]
		titulo = tupla[2]
		if preco != -1:
			preco = preco/100
			print ("\nLink: %s\nTitulo: %s\nPreço: R$ %.2f\n" % (tupla[0], titulo, preco))
		else:
			print ("\nLink: %s\nTitulo: %s\nPreço: INDISPONÍVEL\n" % (tupla[0], titulo))
		
	elif escolha == '4':
		break
	else:
		print ("Escolha inválida.")