#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
diagnostico_busca_global.py  (VERSÃO 100% MANUAL — SÓ GRAVA)
================================================================================
Versão simplificada a pedido do usuário: a tentativa anterior de abrir a
busca global e digitar o nome AUTOMATICAMENTE (via JS/clique no ícone/
Ctrl+Espaço) estava parando antes da hora / não avançando de forma
confiável. Esta versão NÃO tenta automatizar nenhum clique ou digitação --
ela só faz login e depois fica registrando (screenshot + DOM) o estado
atual da tela sempre que você pedir, quantas vezes você quiser.

COMO FUNCIONA
--------------------------------------------------------------------------
1. O script abre o Chrome e faz login no Benner (mesmas credenciais do
   robô principal: variáveis de ambiente BENNER_USUARIO/BENNER_SENHA, ou
   arquivo `benner_credentials.json`).
2. Depois disso, TUDO é feito por você, manualmente, na janela do
   navegador: abrir a busca (Ctrl+Espaço ou clicando na lupa), colar o
   nome do participante, esperar os resultados, clicar em "Pastas", abrir
   a pasta, etc.
3. Sempre que quiser que o estado atual da tela seja gravado (screenshot +
   HTML completo + resumo em JSON), volte ao terminal onde o script está
   rodando, digite um rótulo curto describendo o que está na tela agora
   (ex.: "modal_aberto", "resultados", "pasta_aberta") e pressione ENTER.
   O script grava e imediatamente volta a esperar você fazer a próxima
   ação manual e pedir a próxima gravação.
4. Repita quantas vezes precisar. Para terminar, digite "sair" (ou "s",
   "q", "parar", "exit", "quit") no lugar do rótulo.

Este script NUNCA clica em nada, NUNCA digita nada na tela do Benner, e
NUNCA cadastra ou altera dados -- só grava o que já está na tela.

COMO USAR
--------------------------------------------------------------------------
    python diagnostico_busca_global.py

Sugestão de sequência de rótulos ao usar (mas fique livre para usar os
nomes que quiser):
    1) "antes"            -> antes de abrir a busca
    2) "modal_aberto"     -> depois de abrir a busca (Ctrl+Espaço) e ANTES
                             de digitar o nome
    3) "resultados"       -> depois de colar/digitar o nome e os
                             resultados categorizados aparecerem
    4) "pasta_aberta"     -> depois de clicar em "Pastas" e abrir a pasta
                             encontrada

Os arquivos gerados ficam em:
    <pasta_de_trabalho>/diagnostico_screenshots/   (.png)
    <pasta_de_trabalho>/diagnostico_dom/            (.html e .json)

Onde <pasta_de_trabalho> é:
    Windows -> K:\\BennerData\\CadastraPastas
    macOS   -> /Users/samuelbahia/Downloads/CadastraBenner

Envie de volta os arquivos gerados (HTML + JSON de cada rótulo) para que
a Etapa 2 do robô principal seja implementada com o fluxo real confirmado.
================================================================================
"""

import json
import logging
import os
import platform
import re
import sys
import time
from datetime import datetime
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException


# ==============================================================================
# CONSTANTES
# ==============================================================================
URL_BENNER = "https://previ.bennercloud.com.br/JURIDICO_EXT/jur/e/PREVI.aspx?i=K9_INICIOPREVI&m=MAIN"
LOGIN_URL = "https://previ.bennercloud.com.br/JURIDICO_EXT/Login"
ARQUIVO_CREDENCIAIS = "benner_credentials.json"
WAIT_TIMEOUT = 30


def obter_diretorio_trabalho() -> Path:
    """Mesma convenção de pastas do script principal (cadastro_pastas_benner.py):
      Windows -> K:\\BennerData\\CadastraPastas
      macOS/Linux -> /Users/samuelbahia/Downloads/CadastraBenner
    """
    if platform.system() == "Windows":
        return Path(r"K:\BennerData\CadastraPastas")
    return Path("/Users/samuelbahia/Downloads/CadastraBenner")


def carregar_credenciais(diretorio: "Path | None" = None):
    """Carrega usuario/senha na seguinte ordem:
      1) Variáveis de ambiente BENNER_USUARIO / BENNER_SENHA;
      2) Arquivo JSON local `benner_credentials.json` (na pasta de trabalho
         padrão OU na mesma pasta deste script).
    Retorna (usuario, senha) ou (None, None) se não encontrar nada -- nesse
    caso o login deve ser concluído manualmente na janela do navegador.
    """
    usuario = os.environ.get("BENNER_USUARIO")
    senha = os.environ.get("BENNER_SENHA")
    if usuario and senha:
        return usuario, senha

    candidatos = [diretorio or obter_diretorio_trabalho(), Path(__file__).resolve().parent]
    for pasta in candidatos:
        try:
            caminho = pasta / ARQUIVO_CREDENCIAIS
            if caminho.exists():
                with open(caminho, "r", encoding="utf-8") as f:
                    dados = json.load(f)
                usuario = dados.get("usuario")
                senha = dados.get("senha")
                if usuario and senha:
                    return usuario, senha
        except Exception:
            continue

    return None, None


def configurar_logging(diretorio: Path) -> logging.Logger:
    diretorio.mkdir(parents=True, exist_ok=True)
    log_file = diretorio / f"diagnostico_busca_global_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    logger = logging.getLogger("busca_global")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()
    logger.propagate = False

    fmt = logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    fh = logging.FileHandler(str(log_file), encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    logger.info(f"Log iniciado. Arquivo de log: {log_file}")
    return logger


class GravacaoManual:
    """Login automático + gravação (screenshot/DOM) 100% sob comando do
    usuário. Nenhuma automação de clique/digitação na tela do Benner."""

    def __init__(self, log: logging.Logger):
        self.log = log
        self.driver = None
        self.wait = None

    # --------------------------------------------------------------------
    # Navegador + login (única parte automática deste script)
    # --------------------------------------------------------------------
    def iniciar_navegador(self):
        try:
            options = webdriver.ChromeOptions()
            options.add_argument("--start-maximized")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            self.driver = webdriver.Chrome(options=options)
            self.log.info("Navegador Chrome iniciado.")
        except Exception as e_chrome:
            self.log.warning(f"Falha ao iniciar Chrome ({e_chrome}). Tentando Edge...")
            try:
                options = webdriver.EdgeOptions()
                options.add_argument("--start-maximized")
                self.driver = webdriver.Edge(options=options)
                self.log.info("Navegador Edge iniciado.")
            except Exception as e_edge:
                self.log.error(f"Não foi possível iniciar nenhum navegador: {e_edge}")
                raise RuntimeError(f"Não foi possível iniciar o navegador: {e_edge}")
        self.wait = WebDriverWait(self.driver, WAIT_TIMEOUT)
        self._realizar_login()

    def _localizar_campo_login(self, palavras_chave, tipo="text"):
        try:
            inputs = self.driver.find_elements(By.TAG_NAME, "input")
        except Exception as e:
            self.log.debug(f"Erro ao listar inputs da tela de login: {e}")
            return None
        candidatos_por_tipo = []
        for inp in inputs:
            try:
                input_type = (inp.get_attribute("type") or "text").lower()
                atributos = " ".join(
                    filter(
                        None,
                        [
                            inp.get_attribute("id"),
                            inp.get_attribute("name"),
                            inp.get_attribute("placeholder"),
                            inp.get_attribute("aria-label"),
                        ],
                    )
                )
                atributos_norm = self._normalizar(atributos)
                if any(self._normalizar(p) in atributos_norm for p in palavras_chave):
                    return inp
                if tipo == "password" and input_type == "password":
                    candidatos_por_tipo.append(inp)
                if tipo == "text" and input_type in ("text", "email"):
                    candidatos_por_tipo.append(inp)
            except StaleElementReferenceException:
                continue
        return candidatos_por_tipo[0] if candidatos_por_tipo else None

    @staticmethod
    def _normalizar(texto) -> str:
        import unicodedata
        texto = texto or ""
        texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
        return texto.lower().strip()

    def _realizar_login(self):
        usuario, senha = carregar_credenciais()
        try:
            self.driver.get(LOGIN_URL)
            time.sleep(2)
        except Exception as e:
            self.log.warning(f"Falha ao abrir a página de login ({LOGIN_URL}): {e}")
            return False

        if "login" not in self.driver.current_url.lower():
            self.log.info("Sessão já autenticada — login não foi necessário.")
            return True

        if not usuario or not senha:
            self.log.warning(
                "Nenhuma credencial configurada (env BENNER_USUARIO/BENNER_SENHA "
                f"ou arquivo '{ARQUIVO_CREDENCIAIS}'). Faça o login manualmente na "
                "janela do navegador. Aguardando 45s..."
            )
            time.sleep(45)
            return "login" not in self.driver.current_url.lower()

        campo_usuario = self._localizar_campo_login(
            ["usuario", "usuário", "user", "login", "email", "txtusuario", "txtlogin"], tipo="text"
        )
        campo_senha = self._localizar_campo_login(["senha", "password", "pass", "txtsenha"], tipo="password")

        if not campo_usuario or not campo_senha:
            self.log.warning(
                "Campos de usuário/senha não localizados automaticamente. Faça "
                "o login manualmente na janela do navegador. Aguardando 45s..."
            )
            time.sleep(45)
            return "login" not in self.driver.current_url.lower()

        try:
            campo_usuario.clear()
            campo_usuario.send_keys(usuario)
            campo_senha.clear()
            campo_senha.send_keys(senha)
            campo_senha.send_keys(Keys.RETURN)
            time.sleep(3)
        except Exception as e:
            self.log.warning(f"Falha ao preencher/enviar formulário de login: {e}")
            return False
        return "login" not in self.driver.current_url.lower()

    # --------------------------------------------------------------------
    # DOM Recorder (screenshot + HTML + resumo estruturado em JSON)
    # --------------------------------------------------------------------
    def _capturar_screenshot(self, nome_passo: str):
        try:
            pasta = obter_diretorio_trabalho() / "diagnostico_screenshots"
            pasta.mkdir(parents=True, exist_ok=True)
            nome_seguro = re.sub(r"[^A-Za-z0-9_-]+", "_", nome_passo).strip("_") or "passo"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            caminho = pasta / f"{timestamp}_{nome_seguro}.png"
            self.driver.save_screenshot(str(caminho))
            self.log.info(f"[GRAVAÇÃO] Screenshot salvo: {caminho}")
            return caminho
        except Exception as e:
            self.log.warning(f"[GRAVAÇÃO] Falha ao salvar screenshot ('{nome_passo}'): {e}")
            return None

    def _gravar_dom(self, nome_passo: str):
        """Grava o DOM (HTML completo) da tela atual e um resumo em JSON de
        todos os campos visíveis (input, select, textarea, label, button),
        incluindo opções de <select> e o innerHTML dos painéis de resultado
        da busca global (#searcher-results-items / #searcher-results-entities,
        quando existirem na tela). Salvo em diagnostico_dom/."""
        try:
            pasta = obter_diretorio_trabalho() / "diagnostico_dom"
            pasta.mkdir(parents=True, exist_ok=True)
            nome_seguro = re.sub(r"[^A-Za-z0-9_-]+", "_", nome_passo).strip("_") or "passo"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            caminho_html = pasta / f"{timestamp}_{nome_seguro}.html"
            try:
                html = self.driver.page_source
                caminho_html.write_text(html, encoding="utf-8")
            except Exception as e:
                self.log.debug(f"[DOM RECORDER] Falha ao capturar HTML bruto ('{nome_passo}'): {e}")
                caminho_html = None

            resumo = []
            for tipo in ("input", "select", "textarea", "label", "button"):
                try:
                    elementos = self.driver.find_elements(By.TAG_NAME, tipo)
                except Exception:
                    continue
                for el in elementos:
                    try:
                        item = {
                            "tag": tipo,
                            "id": el.get_attribute("id"),
                            "name": el.get_attribute("name"),
                            "class": el.get_attribute("class"),
                            "type": el.get_attribute("type"),
                            "texto": (el.text or "").strip()[:150],
                            "value": (el.get_attribute("value") or "")[:150],
                            "placeholder": el.get_attribute("placeholder"),
                            "aria_label": el.get_attribute("aria-label"),
                            "visivel": el.is_displayed(),
                            "habilitado": el.is_enabled(),
                        }
                        if tipo == "select":
                            try:
                                item["opcoes"] = [
                                    {"value": o.get_attribute("value"), "texto": o.text}
                                    for o in el.find_elements(By.TAG_NAME, "option")
                                ]
                            except Exception:
                                item["opcoes"] = []
                        if item["id"] or item["name"] or item["texto"] or item["placeholder"] or item["class"]:
                            resumo.append(item)
                    except StaleElementReferenceException:
                        continue
                    except Exception:
                        continue

            # Captura adicional: elementos li/a/div cuja classe pareça ser
            # de resultado de busca (útil para o modal de busca global).
            resultados_busca = []
            for tipo in ("li", "a", "div"):
                try:
                    elementos = self.driver.find_elements(By.TAG_NAME, tipo)
                except Exception:
                    continue
                for el in elementos:
                    try:
                        classe = el.get_attribute("class") or ""
                        texto = (el.text or "").strip()
                        if not texto or len(texto) > 200:
                            continue
                        classe_norm = classe.lower()
                        if any(
                            termo in classe_norm
                            for termo in ("search", "result", "busca", "pasta", "pesquisa")
                        ):
                            resultados_busca.append(
                                {
                                    "tag": tipo,
                                    "id": el.get_attribute("id"),
                                    "class": classe,
                                    "texto": texto[:200],
                                    "href": el.get_attribute("href") if tipo == "a" else None,
                                    "visivel": el.is_displayed(),
                                }
                            )
                    except StaleElementReferenceException:
                        continue
                    except Exception:
                        continue

            # Captura direta dos painéis de resultado da busca global, se
            # existirem na tela atual (confirmados em diagnóstico anterior):
            # #searcher-results-items e #searcher-results-entities.
            paineis_busca = {}
            for painel_id in ("searcher-results-items", "searcher-results-entities"):
                try:
                    el = self.driver.find_element(By.ID, painel_id)
                    paineis_busca[painel_id] = {
                        "innerHTML": self.driver.execute_script("return arguments[0].innerHTML;", el),
                        "texto": el.text,
                        "visivel": el.is_displayed(),
                    }
                except Exception:
                    pass  # painel pode não existir se a busca não estiver aberta

            caminho_json = pasta / f"{timestamp}_{nome_seguro}.json"
            try:
                caminho_json.write_text(
                    json.dumps(
                        {
                            "campos_formulario": resumo,
                            "possiveis_resultados_busca": resultados_busca,
                            "paineis_busca_global": paineis_busca,
                            "url_atual": self.driver.current_url,
                        },
                        ensure_ascii=False,
                        indent=2,
                    ),
                    encoding="utf-8",
                )
            except Exception as e:
                self.log.debug(f"[DOM RECORDER] Falha ao salvar resumo estruturado ('{nome_passo}'): {e}")
                caminho_json = None

            self.log.info(
                f"[DOM RECORDER] '{nome_passo}': "
                f"{('DOM=' + caminho_html.name) if caminho_html else 'DOM=falhou'} | "
                f"{('resumo=' + caminho_json.name) if caminho_json else 'resumo=falhou'} "
                f"({len(resumo)} campos, {len(resultados_busca)} possiveis resultados, "
                f"{len(paineis_busca)} paineis de busca encontrados)"
            )
            return caminho_html, caminho_json
        except Exception as e:
            self.log.warning(f"[DOM RECORDER] Falha geral ao gravar DOM ('{nome_passo}'): {e}")
            return None, None

    def fechar(self):
        if self.driver:
            self.driver.quit()
            self.driver = None
        self.log.info("Execução encerrada.")

    # --------------------------------------------------------------------
    # Loop principal: 100% manual, só grava quando você pedir
    # --------------------------------------------------------------------
    def rodar(self):
        try:
            self.iniciar_navegador()
            self.driver.get(URL_BENNER)
            time.sleep(3)
            self.log.info("=" * 70)
            self.log.info("GRAVAÇÃO MANUAL — nenhuma automação de clique/digitação será feita.")
            self.log.info("Faça tudo manualmente na janela do navegador: abrir a busca")
            self.log.info("(Ctrl+Espaço ou clicando na lupa), colar/digitar o nome, esperar")
            self.log.info("os resultados, clicar em 'Pastas', abrir a pasta, etc.")
            self.log.info("Quando quiser gravar o estado atual da tela, volte aqui, digite")
            self.log.info("um rótulo curto (ex.: 'modal_aberto', 'resultados', 'pasta_aberta')")
            self.log.info("e pressione ENTER. Digite 'sair' para terminar.")
            self.log.info("=" * 70)

            contador = 1
            while True:
                try:
                    rotulo = input(
                        f"\n>>> [{contador:02d}] Rótulo para gravar agora (ou 'sair' para terminar): "
                    ).strip()
                except EOFError:
                    self.log.warning("Entrada não interativa detectada (EOF). Encerrando gravação.")
                    break

                if rotulo.lower() in ("sair", "s", "q", "parar", "exit", "quit"):
                    self.log.info("Encerrando a gravação manual a pedido do usuário.")
                    break

                if not rotulo:
                    rotulo = f"passo_{contador:02d}"

                self._capturar_screenshot(rotulo)
                self._gravar_dom(rotulo)
                contador += 1

            self.log.info("=" * 70)
            self.log.info("FIM DA GRAVAÇÃO MANUAL. Nenhum registro foi criado/alterado no Benner.")
            self.log.info(
                f"Arquivos salvos em: {obter_diretorio_trabalho() / 'diagnostico_dom'} (HTML/JSON) e "
                f"{obter_diretorio_trabalho() / 'diagnostico_screenshots'} (PNG)."
            )
            self.log.info("=" * 70)
        except KeyboardInterrupt:
            self.log.info("GRAVAÇÃO ENCERRADA (Ctrl+C).")
        finally:
            self.fechar()


def main():
    diretorio_trabalho = obter_diretorio_trabalho()
    logger = configurar_logging(diretorio_trabalho)
    logger.info("=" * 60)
    logger.info(" GRAVAÇÃO MANUAL — BUSCA GLOBAL DO BENNER")
    logger.info(" Você controla tudo na tela; o robô só grava quando você pedir.")
    logger.info("=" * 60)

    gravador = GravacaoManual(logger)
    gravador.rodar()


if __name__ == "__main__":
    main()
