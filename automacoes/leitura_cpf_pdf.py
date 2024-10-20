#importando bibliotecas
from PyPDF2 import pyf # Para leitura de PDF
import re # Para captura de padrões

# Caminho para busca pdf e sua leitura
meu_arquivo = r"coloque_nome_arquivo.pdf"
arquivo_pdf = pyf.PdfReader(meu_arquivo)

# contador para captura de numeração de página
i = 1

# lista para captura de cpf
dados = []

# iteração para página por página no PDF
for pagina in arquivo_pdf.pages:
  folha = f'Pagina {i}'
  texto_pagina = pagina.extract_text()
  # captura do padrão de cpf com 11 digitos, onde no trabalho pode haver espaço ou não entre eles * ? significa optativo (pode ou não conter)
  padrao = re.compile(r"\D(\d\s?\s?\s?\d\s?\s?\s?\d\s?\s?\s?\.?\-?\d\s?\s?\s?\d\s?\s?\s?\d\s?\s?\s?\.?\-?\d\s?\s?\s?\d\s?\s?\s?\d\s?\s?\s?\.?\-?\d\s?\s?\s?\d\s?\s?\s?)\D")
  resultado = refindall(padrao, texto_pagina)
  if len(resultado) > 0:
      for item in resultado:
        valores = (folha, item)
        dados.append(valores)

resultado_final = pd.DataFrame(dados, columns=['Página','CPF'])



