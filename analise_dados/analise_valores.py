import pandas as pd # Análise de Dados
import numpy as np # Calculo Numérico
from IPython.display import display, HTML # Visualização no notebook

# =====================================================================================================================
# 0) IMPORTE DA BASE
# =====================================================================================================================

# Importando a base
base = pd.read_excel(r"caminho_excel\base_transacao_financeira.xlsx")

# Garante tipos corretos
base['Valor Líquido'] = pd.to_numeric(base['Valor Líquido'], errors='coerce')

# =====================================================================================================================
# 1) VISÃO GERAL POR LOTE [ Agrupamento por Lote e dentro dele agregação em Documentos Únicos e soma de valor líquido ]
# =====================================================================================================================
df_base = (
    base.groupby('Lote')
        .agg(
            Qtd_Clientes=('Documento', 'nunique'),
            Soma_Valor_Liquido=('Valor Líquido', 'sum')
        )
        .reset_index()
)

df_base['Ticket_Medio'] = round(
    df_base['Soma_Valor_Liquido'] / df_base['Qtd_Clientes'], 2
)

# ====================================================================================================================
# 2) SOMA POR DOCUMENTO [ Dentro de cada lote, soma dos valores líquidos para cada documento ]
# ====================================================================================================================
df_doc_lote = (
    base.groupby(['Lote', 'Documento'])['Valor Líquido']
        .sum()
        .reset_index(name='Soma_Valor_Liquido_Doc')
)

# ===================================================================================================================
# 3) VALOR MAX [ Verifica qual a maior soma de líquido para um mesmo documento no mesmo lote ]
# ===================================================================================================================
lote_max = (
    df_doc_lote.groupby('Lote')['Soma_Valor_Liquido_Doc']
        .max()
        .reset_index(name='Valor_Max')
)

# =================================================================================================================
# 4) JUNÇÃO [ Base com Valor Máximo por Documento em cada lote - renomeando coluna ]
# =================================================================================================================
visao = df_base.merge(lote_max, on='Lote', how='left')

visao = visao.rename(columns={
    'Qtd_Clientes': 'Qtd Clientes',
    'Soma_Valor_Liquido': 'Soma Valor Líquido',
    'Ticket_Medio': 'Ticket Médio',
    'Valor_Max': 'Valor Max/Documento'
})

# ===============================================================================================================
# FORMATADORES [ Funções que formatam os valores e % que estão em string ]
# ===============================================================================================================
def formato_real(x):
    return f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def formato_percentual(x):
    return f"{x*100:.2f}%".replace(".", ",")

# ================================================================================================================
# MÉTRICA [ Objetivo verificar o peso de um documento dentro do lote para classificação de risco ]
# ================================================================================================================
visao['% Cliente no Lote'] = (visao['Valor Max/Documento'] / visao['Ticket Médio'] - 1)

# ================================================================================================================
# CLASSIFICAÇÃO DE RISCO [ Classificação de suspeito de acordo com a regra de negócio ]
# ================================================================================================================
visao['Risco'] = np.where(
    visao['% Cliente no Lote'] > 0.10,
    'Suspeito',
    'Não Suspeito'
)

# ===============================================================================================================
# ORDENAÇÃO [ ordenação do maior para menor de acordo com o risco associado ]
# ===============================================================================================================
visao_ordenada = visao.sort_values(by='% Cliente no Lote', ascending=False)
visao_ordenada = visao_ordenada.reset_index(drop=True)
visao_ordenada.index = visao_ordenada.index + 1

# ===============================================================================================================
# FORMATAÇÃO FINAL [ Melhorar a visualização - usando html e formatação CSS]
# ===============================================================================================================

# HTML estilizado
html = (
    visao_ordenada.style ## aplicação das funções "FORMATADORES" sobre as colunas estipuladas
    .format({
        'Soma Valor Líquido': formato_real,
        'Ticket Médio': formato_real,
        'Valor Max/Documento': formato_real,
        '% Cliente no Lote': formato_percentual
    })
    .set_table_styles([
        {'selector': 'th', 'props': [('background-color', '#1f4e78'), ## aplicação de formatação em CSS do cabeçalho
                                     ('color', 'white'), ## coloração
                                     ('text-align', 'center'), ## alinhamento do texto
                                     ('padding', '8px')]}, ## espaçamento interno da tabulação
        {'selector': 'td', 'props': [('padding', '6px'), ## aplicação de formatação em CSS das linhas
                                     ('text-align', 'center')]}, ## alinhamento do texto
        {'selector': 'table', 'props': [('border-collapse', 'collapse'), ## aplicação de formatação em CSS na estruturação tabela
                                        ('width', '100%'), ## Largura das células
                                        ('font-family', 'Arial, sans-serif'), ## Fonte do texto
                                        ('font-size', '13px')]} ## Tamanho do Texto
    ]) ## aplicação linha a linha de formatação negrito e cor de fundo a depender se for suspeito
    .apply(lambda row: [
        'background-color: #f8d7da; font-weight: bold;' if row['Risco'] == 'Suspeito'
        else 'background-color: #d4edda;'
        for _ in row
    ], axis=1)
)

display(HTML(html.to_html()))
