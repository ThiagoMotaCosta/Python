# Triagem de sinistros suspeitos em seguro auto

> Projeto de portfólio feito com **dados sintéticos**. A seguradora, os números e o contexto são fictícios.

## Contexto
Uma seguradora de automóveis fictícia recebe cerca de 4.000 avisos de sinistro por mês. Uma
pequena parte é fraude: acidentes forjados, danos antigos declarados como novos, valores inflados
e roubos simulados. A **equipe de investigação** consegue analisar só uma fração desses avisos.
Hoje, a escolha de quais avisos investigar segue regras fixas e a experiência dos analistas.

Pagar uma fraude custa à seguradora, em média, o valor do pedido. Investigar um aviso legítimo
custa horas de analista e atrasa o pagamento a um cliente honesto.

## Objetivo
Criar um **score de suspeita** para cada aviso, calculado no momento do registro, que:
1. ordene a fila da equipe de investigação de modo a encontrar o máximo de fraude com a mesma capacidade;
2. permita escolher um ponto de corte com base em custo (fraude paga × investigação desnecessária);
3. explique cada alerta (SHAP), para o analista saber por onde começar a investigação.

## Resultado
Avaliação em **dados nunca vistos**: avisos de dezembro/2025 (4.719 avisos, 156 fraudes). O modelo escolhido é o **LightGBM**, sem as variáveis sensíveis (idade e UF). Ele teve **ROC AUC 0,87** e PR AUC 0,26, cerca de 8 vezes a taxa de fraude da base (3,3%).
Premissas de custo: perícia = R\$ 700; fraude paga = R\$ 20.600 (valor médio pedido nas fraudes).

### Visão financeira (custo mensal = fraudes pagas + perícias)
| Cenário | Perícias | Fraudes encontradas | Custo total | Economia vs. política atual |
|---|---|---|---|---|
| Nenhuma perícia | 0 | 0 | R\$ 3,21 mi | — |
| Política atual (pedidos > R\$ 45 mil) | 356 | 21 (13,5%) | R\$ 3,03 mi | — |
| **Modelo com a equipe atual** (960 maiores scores) | 960 | **114 (73,1%)** | **R\$ 1,54 mi** | **R\$ 1,49 mi (−49%)** |
| **Modelo no ponto ótimo** (limiar 0,54) | 1.025 | **121 (77,6%)** | **R\$ 1,44 mi** | **R\$ 1,59 mi (−53%)** |

- **Sem contratar ninguém**, trocar o critério da fila (valor do pedido → score do modelo) reduz o custo em cerca de **R\$ 1,5 milhão por mês**. Se o padrão se mantiver, isso dá cerca de R\$ 18 milhões por ano.
- A política atual mal se paga: economiza só R\$ 183 mil em relação a não periciar nada, porque 94% das suas perícias não encontram fraude.

### Eficiência da equipe
| Indicador | Política atual | Modelo (mesma equipe) |
|---|---|---|
| Uso da capacidade (960 perícias/mês) | 37% (**604 perícias ociosas**) | 100% |
| Acerto da perícia (fraude encontrada / perícia) | 5,9% | **11,9%** (2×) |
| Fraudes encontradas por mês | 21 | **114** (5,4×) |
| Fraudes pagas sem perícia | 135 | **42** (−69%) |

- O corte por valor desperdiça a equipe: só 356 pedidos passam de R\$ 45 mil no mês, então quase 2/3 dos peritos ficam sem casos. Além disso, a fraude não se concentra nos pedidos mais altos.
- Os **150 primeiros casos da fila do modelo** (5 peritos) têm **35% de acerto**: 53 fraudes, mais que o dobro de tudo o que a política atual encontra.

### Tamanho da equipe
Uma perícia a mais só se paga se encontrar fraude em pelo menos **3,4%** dos casos (R\$ 700 ÷ R\$ 20.600, ou 1 fraude a cada 29 perícias).

| Equipe | Perícias/mês | Fraudes encontradas | Custo total |
|---|---|---|---|
| 32 peritos (atual) | 960 | 114 (73%) | R\$ 1,54 mi |
| **35 peritos (+3), ponto ótimo** | ~1.025 | 121 (78%) | **R\$ 1,44 mi** |
| 64 peritos (dobro) | 1.920 | 144 (92%) | R\$ 1,59 mi |

- **Recomendação:** contratar **3 peritos**, que dão cerca de R\$ 100 mil de economia adicional por mês em relação à equipe atual. Acima disso, o acerto das perícias extras cai abaixo de 3,4% e o custo volta a subir.
- **Dobrar a equipe não dobra o resultado:** são 960 perícias a mais para achar só 30 fraudes a mais (1,26×), e o custo total fica maior que com 35 peritos.
- Na política atual, contratar não adianta nada, porque já faltam casos acima de R\$ 45 mil para os peritos que existem.

### Explicabilidade e conformidade
- **O que mais pesa no score (SHAP):** valor pedido, tipo de sinistro, canal do aviso, ausência de boletim de ocorrência e atraso para avisar. Cada alerta sai com as variáveis que mais o influenciaram, para o perito saber por onde começar.
- **Tirar idade e UF** do segurado (risco de LGPD e de discriminação) não reduziu o desempenho: a diferença de ROC AUC foi menor que 0,005.

> **Limitações:** dados sintéticos e um único mês de teste. O limiar foi escolhido no próprio teste, então a economia no ponto ótimo é uma estimativa otimista. A estimativa anual supõe que o padrão de dezembro se mantém.

## Restrições
- Só podem entrar variáveis **disponíveis no momento do aviso**. Nada que dependa da regulação ou da investigação.
- A validação deve ser **temporal** (treinar no passado e testar no futuro), porque os padrões de fraude mudam com o tempo.
- O desbalanceamento é forte (cerca de 3% de fraude). Por isso as métricas principais são PR-AUC,
  recall dentro da capacidade de investigação e valor de fraude evitado.

## Dados
`data/auto_claims.csv`, com o dicionário em [`data/README.md`](data/README.md).
Para gerar a base de novo:
```bash
python gerar_dados_sinteticos.py --n 50000 --seed 2025
```

## Parâmetros de negócio (Fase 1 do notebook)
- Equipe de perícia: 32 peritos × 30 perícias/mês = **960 perícias/mês**
- Política atual: periciar pedidos **acima de R$ 45 mil**, do maior para o menor, até a capacidade
- Custo da perícia: R$ 700 (com ou sem fraude). Custo da fraude paga: valor médio pedido nas fraudes do treino

## Como rodar
Requer **Python 3.13**.
```bash
pip install -r requirements.txt jupyter
jupyter notebook fraude_auto_claims.ipynb
```
Com 4 núcleos de CPU, a execução completa leva cerca de 6 minutos (a maior parte é o GridSearch).

## Estrutura
```
├── fraude_auto_claims.ipynb    # análise, modelagem, custos e SHAP (CRISP-DM)
├── gerar_dados_sinteticos.py   # gerador da base sintética
├── requirements.txt            # versões testadas das bibliotecas
└── data/
    ├── auto_claims.csv
    └── README.md               # dicionário de dados
```
