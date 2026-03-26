## Financeira [ Procedimento Análise Risco ]

### Case:
Uma empresa do setor Financeiro realiza suas transações e precisa identificar alguma movimentação suspeita para realizar devidos procedimentos de segurança.

### Observação:
Esses dados são totalmente fictícios, assim como esse procedimento que visa somente um exercício de atendimento a uma necessidade hipotética de negócio.

### Planejamento:<br>
1 - Visibilidade dos dados - análise exploratória<br>
2 - Construção de agrupamentos e metrificações conforme verificado no passo 1<br>
3 - Alinhamento das métricas e observaçõe com liderança<br>
4 - Diagnóstico através da análise de dados<br>
5 - Elaboração de um plano de ação voltado ao objetivo do Negócio<br>

**Passo 1: Analise Exploratória**<br>
Visualização da base geral para identificar variáveis e seus padrões<br>
<img src="images/analise_exp_financeira.png" width="300">

**Passo 2: Agrupamento de Documento por Lote**<br>
Identificação de número de documento iguais no mesmo lote e necessidade de uma visão agrupada<br>
<img src="images/analise_exp_finan_agrupada.png" width="400">

**Passo 3: Alinhamento das métricas e observaçõe com liderança**<br>
Após reunião com liderança e observação dos dados, alinhamento de verificar o valor máximo pago ao mesmo documento no lote e verificar a sua representatividade pelo somatório do valor líquido do lote ou número de documento menor que 10 no mesmo lote [ Regrá de Negócio ] - Classificação: Suspeito<br>

**Passo 4: Diagnóstico através da análise de dados**<br>
Verificamos uma variação de número de documentos dentro do mesmo lote (Mínimo: 7 / Máximo: 23), assim como valores Máximos de um documento/lote (Mínimo: 8k / Máximo: 23k) assim sinalizando um desvio de comportamento sobre cada transação<br>
<img src="images/resultado_analise.png" width="700">

**Passo 5: Elaboração de um plano de ação voltado ao objetivo do Negócio**<br>
**1 -** Envio de uma análise minunciosa dos casos classificados como suspeito - realizando contato com devidas área Financeira para rastreabilidade de origem<br>
**2 -** Valores classificados como suspeito, após levantamento minuncioso, será direcionado a liderança com determinados cortes de valores a ser definido pelo negócio para validação antes da efetividade da devida transação<br>

**Codificação:**[Análise Dados](analise_valores.py)<br>
