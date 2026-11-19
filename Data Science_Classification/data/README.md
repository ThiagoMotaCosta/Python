# Dicionário de dados — `auto_claims.csv`

Base **100% sintética** (50.000 avisos de sinistro, ocorrências em 2025, cerca de 3% de fraude),
gerada por `../gerar_dados_sinteticos.py` com seed 2025. Nenhum registro vem de dados reais.

| Coluna | Tipo | Descrição |
|---|---|---|
| `claim_id` | texto | Identificador do aviso de sinistro |
| `incident_date` | data (AAAA-MM-DD) | Data em que o evento ocorreu |
| `incident_time` | texto (HH:MM) | Hora informada do evento |
| `report_date` | data (AAAA-MM-DD) | Data em que o aviso foi registrado na seguradora |
| `report_channel` | categoria | Canal do aviso: `app`, `broker` (corretor), `call_center` |
| `claim_type` | categoria | `collision`, `glass`, `theft`, `third_party_liability`, `flood`, `fire` |
| `state` | categoria | UF de ocorrência |
| `policyholder_age` | inteiro | Idade do segurado, em anos |
| `policy_tenure_days` | inteiro | Dias desde o início da apólice até o evento |
| `prior_claims_12m` | inteiro | Sinistros do segurado nos 12 meses anteriores |
| `vehicle_age` | inteiro | Idade do veículo, em anos |
| `vehicle_market_value` | decimal | Valor de mercado do veículo (referência tabela FIPE), em R$ |
| `claimed_amount` | **texto** | Valor pedido pelo segurado, em R$, com vírgula decimal (ex.: `"4366,13"`) |
| `police_report` | categoria | Boletim de ocorrência apresentado: `yes`, `no`, vazio |
| `third_party_identified` | categoria | Terceiro identificado: `yes`, `no`, `not_applicable` |
| `paid_amount` | decimal | Valor pago **depois** da regulação do sinistro, em R$ |
| `is_fraud` | 0/1 | **Alvo**: 1 = fraude confirmada na investigação |

## Problemas de qualidade incluídos de propósito
- `claimed_amount` vem como texto com vírgula decimal e precisa ser convertido.
- Cerca de 5% de `police_report` está vazio. O campo vazio pode ser tratado como uma categoria própria.
- Alguns valores de `claimed_amount` passam de `vehicle_market_value` (erro de digitação).

## ⚠️ Vazamento de dados
`paid_amount` só é conhecido depois da investigação e quase sempre vale zero quando há fraude.
Usá-lo como variável leva a métricas infladas (AUC por volta de 0,98) que o modelo não alcançaria
em produção. **Não usar como variável do modelo.**
