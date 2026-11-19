"""
Gera uma base SINTÉTICA de sinistros de seguro auto para estudo de detecção de fraude.

Nenhum registro vem de base real: tudo é sorteado a partir de distribuições e
regras definidas neste script. O dicionário de dados está em data/README.md.

Uso:  python gerar_dados_sinteticos.py [--n 50000] [--seed 2025] [--saida data/auto_claims.csv]
"""
import argparse
import numpy as np
import pandas as pd

UFS = {  # peso aproximado da frota por UF
    "SP": 28, "MG": 11, "RJ": 9, "PR": 7, "RS": 7, "SC": 5, "GO": 4, "BA": 4,
    "PE": 3, "CE": 3, "DF": 2.5, "ES": 2, "MT": 2, "PA": 2, "MS": 1.5, "AM": 1,
    "MA": 1, "RN": 1, "PB": 1, "AL": 0.8, "PI": 0.7, "SE": 0.6, "RO": 0.6,
    "TO": 0.5, "AP": 0.2, "AC": 0.2, "RR": 0.2,
}
TIPOS = {  # tipo: (peso, fração média do FIPE reclamada, franquia típica, risco base de fraude)
    "collision":     (50, 0.12, 3200, 1.0),
    "glass":      (21, 0.015, 250, -4.0),
    "theft": (10, 0.97, 0, -1.2),
    "third_party_liability":   (10, 0.10, 0, -1.0),
    "flood":  (6, 0.18, 2800, 0.6),
    "fire":    (3, 0.85, 0, -0.2),
}
CANAIS = {"app": 0.43, "broker": 0.36, "call_center": 0.21}


def gerar(n: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    # --- datas: ocorrências ao longo de 2025, com sazonalidade leve (chuvas no verão)
    dias = pd.date_range("2025-01-01", "2025-12-31", freq="D")
    peso_dia = 1 + 0.15 * np.cos(2 * np.pi * (np.asarray(dias.dayofyear) - 20) / 365)
    data_oc = pd.to_datetime(rng.choice(dias, n, p=peso_dia / peso_dia.sum()))

    tipo = rng.choice(list(TIPOS), n, p=np.array([v[0] for v in TIPOS.values()]) / 100)
    canal = rng.choice(list(CANAIS), n, p=list(CANAIS.values()))
    uf = rng.choice(list(UFS), n, p=np.array(list(UFS.values())) / sum(UFS.values()))

    # hora: pico diurno; roubo/furto concentra mais à noite
    hora = np.clip(rng.normal(14.5, 4.5, n), 0, 23.99)
    noturno = (tipo == "theft") & (rng.random(n) < 0.35)
    hora[noturno] = rng.uniform(0, 6, noturno.sum())
    minuto = rng.integers(0, 60, n)

    idade = np.clip(rng.normal(43, 13, n), 18, 85).round().astype(int)
    dias_apolice = np.clip(rng.gamma(1.6, 650, n), 1, 5000).round().astype(int)
    sinistros_12m = rng.poisson(0.22, n).clip(0, 5)
    idade_veic = np.clip(rng.gamma(2.4, 2.5, n), 0, 25).round().astype(int)
    fipe = np.clip(rng.lognormal(10.95, 0.5, n) * (1 - 0.025 * idade_veic), 12000, 450000)
    fipe = (fipe / 100).round() * 100

    bo = np.where(np.isin(tipo, ["theft", "fire"]), rng.random(n) < 0.95,
                  rng.random(n) < 0.42)
    terceiro = np.where(np.isin(tipo, ["glass", "theft", "flood", "fire"]),
                        "not_applicable", np.where(rng.random(n) < 0.68, "yes", "no"))

    # --- fraude: modelo latente (logístico) com sinais conhecidos do domínio
    risco_tipo = np.array([TIPOS[t][3] for t in tipo])
    noite = (hora < 5)
    z = (
        risco_tipo
        + 1.6 * (dias_apolice < 60) + 0.8 * ((dias_apolice >= 60) & (dias_apolice < 180))
        + 0.7 * (canal == "call_center") - 0.3 * (canal == "broker")
        + 0.9 * (~bo) + 0.5 * (terceiro == "no")
        + 0.35 * sinistros_12m + 0.4 * noite
        + 0.25 * np.log(fipe / 60000)
        + 0.6 * ((idade < 25) & (canal == "call_center"))  # interação
        + rng.normal(0, 0.6, n)
    )
    # intercepto calibrado para ~3% de fraude
    lo, hi = -15.0, 5.0
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if (1 / (1 + np.exp(-(z + mid)))).mean() < 0.03 else (lo, mid)
    fraude = (rng.random(n) < 1 / (1 + np.exp(-(z + mid)))).astype(int)

    # atraso na abertura do aviso (fraudes demoram um pouco mais)
    atraso = rng.geometric(np.where(fraude == 1, 0.30, 0.48), n) - 1
    atraso = np.minimum(atraso, 45)
    data_ab = data_oc + pd.to_timedelta(atraso, unit="D")

    # valor reclamado: fração do FIPE por tipo; fraudes inflam o pedido
    frac = np.array([TIPOS[t][1] for t in tipo])
    total = np.isin(tipo, ["theft", "fire"])
    pedido = np.where(total, fipe * rng.uniform(0.85, 1.0, n),
                      fipe * frac * rng.lognormal(0, 0.8, n))
    pedido = np.where(fraude == 1, pedido * rng.uniform(1.4, 3.0, n), pedido)
    pedido = np.minimum(pedido, fipe)
    # ruído de qualidade: ~0,2% dos pedidos acima do FIPE (erro de digitação)
    erro = rng.random(n) < 0.002
    pedido[erro] = fipe[erro] * rng.uniform(1.05, 3.0, erro.sum())
    pedido = np.maximum(pedido, 80).round(2)

    # valor indenizado (pós-regulação): fraude quase sempre zerada -> VAZAMENTO proposital
    franquia = np.array([TIPOS[t][2] for t in tipo]) * rng.uniform(0.8, 1.2, n)
    indeniz = np.maximum(pedido - franquia, 0)
    negado = rng.random(n) < 0.10
    indeniz[negado] = 0
    f = fraude == 1
    indeniz[f] = np.where(rng.random(f.sum()) < 0.93, 0, indeniz[f] * rng.uniform(0, 0.3, f.sum()))
    indeniz = indeniz.round(2)

    # boletim: ~5% ausente (campo não preenchido)
    bo_txt = np.where(bo, "yes", "no").astype(object)
    bo_txt[rng.random(n) < 0.05] = None

    ids = rng.choice(np.arange(100000, 999999), n, replace=False)
    df = pd.DataFrame({
        "claim_id": [f"CLM-{i}" for i in ids],
        "incident_date": data_oc.strftime("%Y-%m-%d"),
        "incident_time": [f"{int(h):02d}:{m:02d}" for h, m in zip(hora, minuto)],
        "report_date": data_ab.strftime("%Y-%m-%d"),
        "report_channel": canal,
        "claim_type": tipo,
        "state": uf,
        "policyholder_age": idade,
        "policy_tenure_days": dias_apolice,
        "prior_claims_12m": sinistros_12m,
        "vehicle_age": idade_veic,
        "vehicle_market_value": fipe,
        # exportado de sistema brasileiro: vírgula decimal, como texto
        "claimed_amount": [f"{v:.2f}".replace(".", ",") for v in pedido],
        "police_report": bo_txt,
        "third_party_identified": terceiro,
        "paid_amount": indeniz,
        "is_fraud": fraude,
    })
    return df.sample(frac=1, random_state=seed).reset_index(drop=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=50000)
    ap.add_argument("--seed", type=int, default=2025)
    ap.add_argument("--saida", default="data/auto_claims.csv")
    a = ap.parse_args()
    df = gerar(a.n, a.seed)
    df.to_csv(a.saida, index=False)
    print(f"{len(df)} linhas salvas em {a.saida} | taxa de fraude = {df.is_fraud.mean():.2%}")
