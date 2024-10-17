# Importando a bliblioteca para análise de dados
import pandas as pd

# Importando a base a ser analisada
base = pd.read_excel("C:/Users/Samsung/OneDrive/Documentos/arquivo.xlsx")

# lista para a separação dos valores em lotes para análise 
resultado_lote = []

#Iteração nos lotes para cálculo dos valores
for i in range(len(base['Lote'].unique())):
    lote_unico = base['Lote'].unique()[i]
    qtd_documento = base.loc[base['Lote'] == lote_unico]['Documento'].unique()
    qtd_documento = len(qtd_documento)
    soma_liquida = base.loc[base['Lote'] == lote_unico]['Valor Líquido'].sum()
    ticket_medio = round(soma_liquida / qtd_documento, 2)
    valores = (lote_unico, qtd_documento, soma_liquida, ticket_medio)
    resultado_lote.append(valores)

# Transformação da lista valores em DataFrame
df_base = pd.DataFrame(resultado_lote, columns = ['Lote', 'Qtd Clientes', 'Soma Valor Líquido', 'Ticket Médio'])

#Busca de valores máximos de valor líquido por Documento
maximo = []
for i in range(len(base['Documento'].unique())):
    doc = base['Documento'].unique()[i]
    if len(base.loc[base['Documento']==doc]['Lote'].unique()) > 1:
        lote_primeiro = base.loc[base['Documento']==doc]['Lote'].unique()[1]
        soma_liquida = base.loc[(base['Documento']==doc) & (base['Lote']==lote_primeiro)]['Valor Líquido'].sum()
        valores = (lote_primeiro, doc, soma_liquida)
        maximo.append(valores)
    lote_unico = base.loc[base['Documento']==doc]['Lote'].unique()[0]
    soma_liquida = base.loc[(base['Documento']==doc) & (base['Lote']==lote_unico)]['Valor Líquido'].sum()
    valores = (lote_unico, doc, soma_liquida)
    maximo.append(valores)

# Transformação da lista maximo valores documento em DataFrame
df_max_valor_doc_lote = pd.DataFrame(maximo, columns = ['Lote', 'Documento', 'Soma Valor Líquido'])

# Separa os valores máximos por lote e documento
lote_max = []
for i in range(len(df_max_valor_doc_lote['Lote'])):
    lote = df_max_valor_doc_lote['Lote'][i]
    valor_max = df_max_valor_doc_lote.loc[df_max_valor_doc_lote['Lote']==lote]['Soma Valor Líquido'].max()
    valores = (lote,valor_max)
    lote_max.append(valores)

# Transformando lote maximo em DataFrame
lote_max = pd.DataFrame(lote_max, columns = ['Lote', 'Valor Max'])

# Adicionando a coluna de valor máximo de documento no lote no primeiro DataFrame
visao = df_base.merge(lote_max, on = 'Lote', how = 'left') 

# Visualização do DataFrame com retirada de duplicadas
visao = visao.drop_duplicates()
visao
