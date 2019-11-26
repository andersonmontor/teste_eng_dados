# Este arquivo tem como objetivo fazer a extração dos dados relevantes contidos nas paginas dos links fornecidos




# link de página do Mercado Livre -> tupla de dados
def extrai_dados_ML(ml_link):
	pass 
	
	
# arquivo CSV -> faz a extração em todos os links usando multithreading para coleta rapida
# embora python não suporte multi-processamento, as chamadas são bloqueadoras por IO(rede),
# então se consegue um aumento de desempenho significante
def extrai_todos(csv_path):
	erros = []
	