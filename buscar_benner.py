# ══════════════════════════════════════════════════════════
# USO:
#   pip install requests pandas
#   python buscar_benner.py
#
# Os CSVs serão salvos em PASTA_SAIDA (padrão: C:\BennerData)
# Para atualização automática, agende via Agendador de Tarefas do Windows
# ══════════════════════════════════════════════════════════

import requests
import pandas as pd
import os

# ══════════════════════════════════════════════════════════
# CONFIGURAÇÕES
# ──────────────────────────────────────────────────────────
# As credenciais podem ser definidas como variáveis de
# ambiente para evitar expô-las no código-fonte:
#
#   Windows (PowerShell):
#     $env:BENNER_USUARIO = "meu_usuario"
#     $env:BENNER_SENHA   = "minha_senha"
#
#   Linux/macOS:
#     export BENNER_USUARIO="meu_usuario"
#     export BENNER_SENHA="minha_senha"
#
# Se as variáveis de ambiente não estiverem definidas, os
# valores padrão abaixo serão usados como fallback.
# ══════════════════════════════════════════════════════════
BASE_URL      = os.environ.get("BENNER_BASE_URL",      "https://previ.bennercloud.com.br/JURIDICO")
USUARIO       = os.environ.get("BENNER_USUARIO",       "SEU_USUARIO")
SENHA         = os.environ.get("BENNER_SENHA",         "SUA_SENHA")
CLIENT_ID     = os.environ.get("BENNER_CLIENT_ID",     "Swagger")
CLIENT_SECRET = os.environ.get("BENNER_CLIENT_SECRET", "N/A")

# Pasta onde os CSVs serão salvos — Power BI vai ler daqui
# Pode ser configurado via variável de ambiente BENNER_PASTA_SAIDA
PASTA_SAIDA   = os.environ.get("BENNER_PASTA_SAIDA", r"C:\BennerData")

# Lista completa de datasources K_
K_DATASOURCES = [
    "K_MODELOESTATISTICOCOMPARATIVOCONDENACOESPROVISOES",
    "K_PROCESSOSCAPECGEBEN",
    "K_ID_PAGAMENTOS_LIQUIDACAO_MENSAL",
    "K_RELATORIOGESOPINADIMPLENCIAFILTROPREVIAUTORA",
    "K_PROCESSOSPARADOSMAISDE60DIASPREVI",
    "K_FLUXOSUSPENSOERRO",
    "K_RESUMOPASTASGESOP",
    "K_BASEDEBLOQUEIOSPORPLANOEPROGRAMA",
    "K_DECISOESPREVI",
    "K_SEGUROSGARANTIA",
    "K_ACJSPREVIV2025GDP",
    "K_VALORESPROVISIONADOSPORPLANOEPROGRAMA2024",
    "K_BASETOTALDEPROCESSOSENCERRADOS2024",
    "K_BASEDEPEDIDOSPORPLANOEPROGRAMA2024",
    "K_BASEDEPEDIDOSPORPLANOEPROGRAMA",
    "K_BASETOTALDEPROCESSOS",
    "K_VALORESPROVISIONADOSPORPLANOEPROGRAMA",
    "K_RELATORIOGERAI",
    "K_BACKTESTGECAT",
    "K_CONSULTADECPEDPUB",
    "K_HONORARIOS",
    "K_TAREFASPREVI",
    "K_RELATORIOGESOPINADIMPLENCIA",
    "K_RESUMODASPASTAS",
    "K_CONSULTASSTATUSTAREFASGECAT",
    "K_BASEDEPARECERES",
    "K_USUARIOSATIVOSCOMGRUPO",
    "K_CONTROLEDELICENCADEUSUARIOS",
    "K_BASETAREFASPORRESPONSAVEL",
    "K_BASEDURACAOMEDIAEXECUCAOWFL",
    "K_BASESLATAREFAS30DIAS",
    "K_BASESLATAREFAS",
    "K_BASEPROVISOES",
    "K_BASEFINANCEIRO",
    "K_BASEDEPASTAS",
    "K_BASEDEDECISOES",
    "K_BASEDEMOVIMENTOSDEDEPOSITOS",
    "K_BASEDEDEPOSITOS",
    "K_BASEDEPEDIDOS",
    "K_BASEDEPARTICIPANTES",
    "K_BASEDEPROCESSOS",
]

# ══════════════════════════════════════════════════════════
# FUNÇÕES
# ══════════════════════════════════════════════════════════
def obter_token():
    url  = f"{BASE_URL}/app_services/auth.oauth2.svc/token"
    data = {
        "grant_type"   : "password",
        "username"     : USUARIO,
        "password"     : SENHA,
        "client_id"    : CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    try:
        resp = requests.post(url, data=data, timeout=30)
        resp.raise_for_status()
        token = resp.json()["access_token"]
        print("✅ Token obtido com sucesso!")
        return token
    except Exception as e:
        print(f"❌ Erro ao obter token: {e}")
        raise


def buscar_datasource(token, key):
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept"       : "application/json"
    }
    url = f"{BASE_URL}/api/datasources/{key}"
    try:
        resp = requests.get(url, headers=headers, timeout=60)
        if resp.status_code == 200:
            dados = resp.json()
            if isinstance(dados, list):
                return pd.DataFrame(dados), None
            elif isinstance(dados, dict):
                for campo in ["data", "items", "value", "result", "records"]:
                    if campo in dados and isinstance(dados[campo], list):
                        return pd.DataFrame(dados[campo]), None
                return pd.DataFrame([dados]), None
            else:
                return pd.DataFrame(), f"Formato inesperado: {type(dados)}"
        else:
            return pd.DataFrame(), f"HTTP {resp.status_code}: {resp.text[:200]}"
    except Exception as e:
        return pd.DataFrame(), str(e)


def salvar_csv(df, key):
    os.makedirs(PASTA_SAIDA, exist_ok=True)
    caminho = os.path.join(PASTA_SAIDA, f"{key}.csv")
    df.to_csv(caminho, index=False, encoding="utf-8-sig")
    return caminho


# ══════════════════════════════════════════════════════════
# EXECUÇÃO
# ══════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 60)
    print("  Benner → Power BI   |   Extrator de Datasources K_")
    print(f"  Total de datasources: {len(K_DATASOURCES)}")
    print("=" * 60)

    token = obter_token()

    resultados = []
    for i, key in enumerate(K_DATASOURCES, start=1):
        print(f"\n[{i:02d}/{len(K_DATASOURCES)}] ⏳ Buscando {key}...")
        df, erro = buscar_datasource(token, key)

        if not df.empty:
            caminho = salvar_csv(df, key)
            print(f"  ✅ {len(df)} linhas x {len(df.columns)} colunas → {caminho}")
            resultados.append({
                "datasource": key,
                "linhas"    : len(df),
                "colunas"   : len(df.columns),
                "arquivo"   : caminho,
                "status"    : "OK",
                "erro"      : ""
            })
        else:
            print(f"  ❌ Vazio ou erro: {erro}")
            resultados.append({
                "datasource": key,
                "linhas"    : 0,
                "colunas"   : 0,
                "arquivo"   : "",
                "status"    : "ERRO",
                "erro"      : erro or "Retornou vazio"
            })

    # ── Salva resumo ──────────────────────────────────────
    os.makedirs(PASTA_SAIDA, exist_ok=True)
    resumo = pd.DataFrame(resultados)
    resumo.to_csv(os.path.join(PASTA_SAIDA, "_RESUMO.csv"), index=False, encoding="utf-8-sig")

    # ── Relatório final ───────────────────────────────────
    ok   = resumo[resumo["status"] == "OK"]
    erro = resumo[resumo["status"] == "ERRO"]

    print("\n" + "=" * 60)
    print(f"  ✅ Sucesso : {len(ok):02d} datasources")
    print(f"  ❌ Erro    : {len(erro):02d} datasources")
    print(f"  📁 Pasta   : {PASTA_SAIDA}")
    print("=" * 60)

    if not erro.empty:
        print("\n⚠️  Datasources com erro:")
        for _, row in erro.iterrows():
            print(f"  • {row['datasource']}: {row['erro']}")

    print(f"\n✅ Resumo salvo em: {os.path.join(PASTA_SAIDA, '_RESUMO.csv')}")
    print("=" * 60)
