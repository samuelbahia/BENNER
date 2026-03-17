# =============================================================================
# buscar_benner.py — Extrator de datasources K_ da API Benner Jurídico
# =============================================================================
#
# USO:
#   pip install requests pandas tqdm
#   python buscar_benner.py
#
# Credenciais podem ser passadas via variáveis de ambiente:
#   set BENNER_USUARIO=meu.usuario   (Windows)
#   set BENNER_SENHA=minha_senha
#   python buscar_benner.py
#
# Ou editando diretamente as variáveis USUARIO e SENHA abaixo.
# Os CSVs serão salvos em PASTA_SAIDA (padrão: C:\BennerData)
# Para atualização automática, agende via Agendador de Tarefas do Windows
#
# =============================================================================

import os
import csv
import json
import traceback
import concurrent.futures
from datetime import datetime

import requests
import pandas as pd

# ── Barra de progresso (opcional) ────────────────────────────────────────────
try:
    from tqdm import tqdm
    _TQDM_AVAILABLE = True
except ImportError:
    _TQDM_AVAILABLE = False

    class tqdm:  # fallback no-op
        def __init__(self, iterable=None, total=None, desc=None, **kwargs):
            self._iterable = iterable
            self._total = total
            self._desc = desc
            self._count = 0
            if desc:
                print(f"[{desc}] iniciando...")

        def __iter__(self):
            for item in self._iterable:
                yield item

        def update(self, n=1):
            self._count += n

        def close(self):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            self.close()


# =============================================================================
# ── CONFIGURAÇÕES ─────────────────────────────────────────────────────────────
# =============================================================================

BASE_URL      = "https://previ.bennercloud.com.br/JURIDICO"
USUARIO       = os.getenv("BENNER_USUARIO", "SEU_USUARIO")   # ou defina aqui
SENHA         = os.getenv("BENNER_SENHA",   "SUA_SENHA")     # ou defina aqui
CLIENT_ID     = "Swagger"
CLIENT_SECRET = "N/A"

PASTA_SAIDA   = r"C:\BennerData"     # pasta onde os CSVs serão salvos
MAX_WORKERS   = 5                    # threads simultâneas
TIMEOUT       = 60                   # segundos por requisição

# Lista completa de datasources K_
DATASOURCES = [
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


# =============================================================================
# ── AUTENTICAÇÃO ──────────────────────────────────────────────────────────────
# =============================================================================

def obter_token():
    """Autentica na API Benner via OAuth2 ROPC e retorna o access_token."""
    token_url = f"{BASE_URL}/app_services/auth.oauth2.svc/token"
    payload = {
        "grant_type"   : "password",
        "username"     : USUARIO,
        "password"     : SENHA,
        "client_id"    : CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    print("🔐 Autenticando na API Benner...")
    try:
        resp = requests.post(token_url, data=payload, timeout=TIMEOUT)
        resp.raise_for_status()
        token = resp.json().get("access_token")
        if not token:
            raise ValueError(
                f"Campo 'access_token' não encontrado na resposta: {resp.text[:300]}"
            )
        print("✅ Token obtido com sucesso.")
        return token
    except requests.HTTPError as exc:
        raise RuntimeError(
            f"❌ Falha na autenticação HTTP {exc.response.status_code}: "
            f"{exc.response.text[:300]}"
        ) from exc
    except Exception as exc:
        raise RuntimeError(f"❌ Falha na autenticação: {exc}") from exc


# =============================================================================
# ── BUSCA DE DATASOURCE ───────────────────────────────────────────────────────
# =============================================================================

def _extrair_registros(dados):
    """
    Normaliza a resposta da API para uma lista de dicionários.

    Formatos suportados:
      - Lista direta:          [{...}, {...}]
      - Objeto com chave data: {"data": [...]}
      - Outras chaves comuns:  items | value | result | records
      - Objeto único:          {...}  →  [{...}]
    """
    if isinstance(dados, list):
        return dados

    if isinstance(dados, dict):
        for chave in ("data", "items", "value", "result", "records"):
            if chave in dados and isinstance(dados[chave], list):
                return dados[chave]
        # objeto único → transforma em lista de 1 linha
        return [dados]

    return []


def buscar_datasource(key, token):
    """
    Busca um datasource K_ e retorna um DataFrame.
    """
    url = f"{BASE_URL}/api/datasources/{key}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept"       : "application/json",
    }
    resp = requests.get(url, headers=headers, timeout=TIMEOUT)
    resp.raise_for_status()

    dados = resp.json()
    registros = _extrair_registros(dados)

    if not registros:
        return pd.DataFrame()

    return pd.DataFrame(registros)


# =============================================================================
# ── SALVAMENTO ────────────────────────────────────────────────────────────────
# =============================================================================

def salvar_csv(df, key, pasta):
    """Salva o DataFrame como CSV com encoding utf-8-sig."""
    os.makedirs(pasta, exist_ok=True)
    caminho = os.path.join(pasta, f"{key}.csv")
    df.to_csv(caminho, index=False, encoding="utf-8-sig")
    return caminho


# =============================================================================
# ── WORKER (executado em paralelo) ───────────────────────────────────────────
# =============================================================================

def processar_datasource(key, token, pasta):
    """
    Busca, converte e salva um datasource.

    Retorna um dicionário com o resultado para o resumo.
    """
    resultado = {
        "datasource": key,
        "linhas"    : 0,
        "colunas"   : 0,
        "arquivo"   : "",
        "status"    : "ERRO",
        "erro"      : "",
    }
    try:
        df = buscar_datasource(key, token)
        caminho = salvar_csv(df, key, pasta)
        resultado.update({
            "linhas"  : len(df),
            "colunas" : len(df.columns),
            "arquivo" : caminho,
            "status"  : "OK",
            "erro"    : "",
        })
        print(f"  ✅ {key}: {len(df)} linhas × {len(df.columns)} colunas")
    except Exception:
        linhas_tb = traceback.format_exc().strip().splitlines()
        erro_msg = linhas_tb[-1] if linhas_tb else "Erro desconhecido"
        resultado["erro"] = erro_msg
        print(f"  ❌ {key}: {erro_msg}")
    return resultado


# =============================================================================
# ── RESUMO ────────────────────────────────────────────────────────────────────
# =============================================================================

def salvar_resumo(resultados, pasta):
    """Salva _RESUMO.csv com status de cada datasource."""
    os.makedirs(pasta, exist_ok=True)
    caminho = os.path.join(pasta, "_RESUMO.csv")
    campos = ["datasource", "linhas", "colunas", "arquivo", "status", "erro"]
    with open(caminho, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(resultados)
    return caminho


# =============================================================================
# ── MAIN ──────────────────────────────────────────────────────────────────────
# =============================================================================

def main():
    inicio = datetime.now()
    print("=" * 60)
    print("  Extrator Benner Jurídico — datasources K_")
    print(f"  Início: {inicio.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 1. Autenticação
    token = obter_token()

    # 2. Busca paralela
    print(f"\n📥 Buscando {len(DATASOURCES)} datasources "
          f"(workers={MAX_WORKERS})...\n")

    resultados = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(processar_datasource, key, token, PASTA_SAIDA): key
            for key in DATASOURCES
        }

        with tqdm(total=len(futures), desc="Progresso", unit="ds") as barra:
            for future in concurrent.futures.as_completed(futures):
                resultados.append(future.result())
                barra.update(1)

    # Ordena pelo nome do datasource para facilitar leitura do resumo
    resultados.sort(key=lambda r: r["datasource"])

    # 3. Resumo
    caminho_resumo = salvar_resumo(resultados, PASTA_SAIDA)

    # 4. Estatísticas finais
    ok    = sum(1 for r in resultados if r["status"] == "OK")
    erro  = len(resultados) - ok
    fim   = datetime.now()
    duracao = (fim - inicio).total_seconds()

    print("\n" + "=" * 60)
    print(f"  ✅ Concluídos com sucesso : {ok}")
    print(f"  ❌ Erros                  : {erro}")
    print(f"  📁 Pasta de saída        : {PASTA_SAIDA}")
    print(f"  📄 Resumo                : {caminho_resumo}")
    print(f"  ⏱  Duração               : {duracao:.1f}s")
    print("=" * 60)


if __name__ == "__main__":
    main()


# =============================================================================
# ── POWER QUERY M — Template para leitura no Power BI ─────────────────────────
# =============================================================================
#
# // Template Power Query para cada K_
# // Obter Dados → Texto/CSV → selecione o arquivo em C:\BennerData\
# //
# // Substitua K_BASEDEPROCESSOS pelo nome do datasource desejado.
#
# let
#     Fonte = Csv.Document(
#         File.Contents("C:\BennerData\K_BASEDEPROCESSOS.csv"),
#         [
#             Delimiter   = ",",
#             Columns     = null,
#             Encoding    = 65001,   // UTF-8
#             QuoteStyle  = QuoteStyle.Csv
#         ]
#     ),
#     TabelaComCabecalho = Table.PromoteHeaders(Fonte, [PromoteAllScalars = true])
# in
#     TabelaComCabecalho
#
# =============================================================================
