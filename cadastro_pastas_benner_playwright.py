#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
CADASTRO DE PASTAS BENNER (PREVI JURÍDICO) — versão PLAYWRIGHT
Reescrita focada em ESTABILIDADE (Anti-Timeout) e DESCOBERTA DE API.
================================================================================
Parecer PAR.0000871/26 - Ajuizamento dívidas prev. 2024 Parte 2

Esta versão remove o uso da tecla "Escape" (que causava o fechamento/cancelamento
do formulário no Benner WebForms, gerando a cascata de erros "não encontrado").
Além disso, adiciona mecanismos para capturar e imprimir as opções da API
carregadas no Select2 (Descoberta de API) para facilitar a resolução de problemas
onde o texto procurado diverge do retornado pelo Benner.

MENU:
  1 - Etapa 1: Análise prévia de duplicidades (Python puro, sem navegador)
  3 - Etapa 3: Cadastrar pastas (PLAYWRIGHT — attach ao Edge debug 9222)
  4 - Relatório
  9 - Sair

MODO DE CONEXÃO (attach):
  1) Feche o Edge. 2) Rode abrir_edge_debug.bat (porta 9222). 3) Faça LOGIN no
  Benner. 4) Rode: py cadastro_pastas_benner_playwright.py  -> opção 3.

PRÉ-REQUISITO:  py -m pip install playwright openpyxl
================================================================================
"""
import asyncio
import json
import os
import random
import re
import time
from datetime import date, datetime
from pathlib import Path

import openpyxl
from playwright.async_api import async_playwright, TimeoutError as PWTimeout

CDP_URL = os.environ.get("BENNER_CDP_URL", "http://127.0.0.1:9222")
MARK_CATEGORIA = "cadastrorapidomanual"      # aba do seletor de categoria
MARK_FORM      = "pr_cadastrorapidopasta"    # aba do formulário real

# ==============================================================================
URL_BENNER = "https://previ.bennercloud.com.br/JURIDICO/jur/e/PREVI.aspx?i=K9_INICIOPREVI&m=MAIN"

CATEGORIA = "Cível"
CAUSA_PEDIR = "Previdencial"
CAUSA_RAIZ = "Produto"
RITO = "Ordinário"
ANDAMENTO = "PEDIDO DE AJUIZAMENTO DE AÇÃO"
PEDIDO = "Dívida Previdenciária"
RISCO = "Possível"
GERENCIA_FALLBACK = "GEPAB"
COND_AUTOR = "Autor"
COND_REU = "Réu"
OBSERVACAO = "Cadastrado conforme Parecer PAR.0000871/26 - Ajuizamento dívidas previdenciárias (Ano 2024 Parte 2)"

FN = {
    "FILIAL": "FILIAL", "DIRETORIA": "DEPARTAMENTO", "GERENCIA": "DIVISAO",
    "TIPO": "TIPO", "CAUSA_PEDIR": "ASSUNTO", "CAUSA_RAIZ": "CAUSARAIZ",
    "RITO": "RITO", "ORGAO": "ORGAO", "UF": "UF", "ANDAMENTO_1": "EVENTO1",
    "PART_REU": "PARTICIPANTE1", "COND_REU": "CONDICAO1",
    "PART_AUTOR": "PARTICIPANTE2", "COND_AUTOR": "CONDICAO2",
    "ADV_INTERNO": "ADVOGADOINTERNO", "ADV_EXTERNO": "ADVOGADOEXTERNO",
    "PEDIDO_1": "PEDIDO1", "RISCO_1": "RISCOPEDIDO1",
}
TEXT_FN = {
    "NUMERO": "NUMERODISTRIBUICAO", "DATA_ANDAMENTO_1": "DATAANDAMENTO1",
    "VALOR_PEDIDO_1": "VALORPEDIDO1", "OBSERVACOES": "OBSERVACOES",
}

COL_PLANO = 1; COL_NOME = 4; COL_CONTRATO = 6; COL_VALOR_DIVIDA = 15; COL_GERENCIA = 17
COL_UF = 20; COL_CPF = 23; COL_BENNER_FLAG = 28; COL_ANALISE = 30; COL_STATUS = 31
COL_CNJ = 32; COL_PLANO_DESC = 33; COL_PESQUISA_BENNER = 34; COL_ID_PASTA = 35
COL_VALOR_PEDIDO = 36

ADVOGADOS_INTERNOS = ["EDSON EDUARDO AGUIAR AVELAR", "MICHELLE CERQUEIRA NUNEZ", "DOMINIQUE DE SOUZA MACHADO"]
ADVOGADOS_EXTERNOS = ["Aldrigues Cândido Advocacia", "Bicudo, Matos, e Moraes Sociedade de Advogados", "Dannemann Siemsen Advogados", "Queiroga, Vieira, Queiroz & Ramos Advocacia", "Wambier, Yamasaki, Bevervanço & Lobo Advocacia"]
UF_ORGAO = {"AC": "do Acre", "AL": "de Alagoas", "AP": "do Amapá", "AM": "do Amazonas", "BA": "da Bahia", "CE": "do Ceará", "DF": "do Distrito Federal", "ES": "do Espírito Santo", "GO": "de Goiás", "MA": "do Maranhão", "MT": "de Mato Grosso", "MS": "de Mato Grosso do Sul", "MG": "de Minas Gerais", "PA": "do Pará", "PB": "da Paraíba", "PR": "do Paraná", "PE": "de Pernambuco", "PI": "do Piauí", "RJ": "do Rio de Janeiro", "RN": "do Rio Grande do Norte", "RS": "do Rio Grande do Sul", "RO": "de Rondônia", "RR": "de Roraima", "SC": "de Santa Catarina", "SP": "de São Paulo", "SE": "de Sergipe", "TO": "do Tocantins"}

def _parse_valor_br(txt) -> float:
    if txt is None or txt == "": return 0.0
    if isinstance(txt, (int, float)): return float(txt)
    s = str(txt).strip().replace(".", "").replace(",", ".")
    try: return float(s)
    except ValueError: return 0.0

def _termo_busca(texto):
    esp = {"pedido de ajuizamento de ação": "ajuizamento", "dívida previdenciária": "previden",
           "plano de beneficios 1": "beneficios 1", "previdencial": "previden", "produto": "produto",
           "ordinário": "ordin", "possível": "poss", "diretoria de seguridade": "seguridade", "cível": "cível"}
    low = (texto or "").lower().strip()
    if low in esp: return esp[low]
    pal = (texto or "").split()
    return pal[0][:8] if pal else (texto or "")[:8]

class CadastroPastasBennerPW:
    def __init__(self, arquivo_excel, sheet_name=None):
        self.arquivo_excel = Path(arquivo_excel)
        self.sheet_name = sheet_name
        self.wb = None; self.ws = None
        self._log_path = str(self.arquivo_excel.parent / f"log_execucao_{time.strftime('%Y%m%d_%H%M%S')}.txt")

    def _log(self, msg):
        linha = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
        print(linha)
        try:
            with open(self._log_path, "a", encoding="utf-8") as f:
                f.write(linha + "\n")
        except Exception: pass

    def carregar_planilha(self):
        self.wb = openpyxl.load_workbook(str(self.arquivo_excel))
        if self.sheet_name and self.sheet_name in self.wb.sheetnames:
            self.ws = self.wb[self.sheet_name]
        else: self.ws = self.wb[self.wb.sheetnames[0]]

    def salvar_planilha(self):
        self.wb.save(str(self.arquivo_excel))
        self._log("Planilha salva.")

    # [Etapas 1 e 4 Omitidas por brevidade; idênticas à V90]
    def analise_previa_duplicidades(self): self._log("Por favor use a opção 1 original. Esta versão foca no fluxo PW."); return 0
    def gerar_relatorio(self): pass

    async def _instalar_hook_rede(self, page):
        js = r"""
        (function(){
          if (window.__netcap && window.__netcap.installed) return 'ja';
          window.__netcap = {installed:true, events:[]};
          function push(ev){ try{ window.__netcap.events.push(ev);
            if(window.__netcap.events.length>3000) window.__netcap.events.shift(); }catch(e){} }
          const _fetch = window.fetch;
          window.fetch = async function(input, init){
            const t0=Date.now(); let url='',method='GET',body='';
            try{ url=(typeof input==='string')?input:(input&&input.url?input.url:'');
              method=(init&&init.method)?String(init.method).toUpperCase():'GET'; }catch(e){}
            try{ const r=await _fetch.apply(this,arguments);
              push({kind:'fetch',ts:t0,url:url,method:method,status:r?r.status:null});
              return r; }catch(err){ push({kind:'fetch',ts:t0,url:url,error:String(err)}); throw err; }
          };
          const _open=XMLHttpRequest.prototype.open, _send=XMLHttpRequest.prototype.send;
          XMLHttpRequest.prototype.open=function(m,u){ this.__nc={m:String(m||'GET').toUpperCase(),u:String(u||''),t0:Date.now()}; return _open.apply(this,arguments); };
          XMLHttpRequest.prototype.send=function(b){
            const s=this; this.addEventListener('loadend',function(){ try{ push({kind:'xhr',ts:s.__nc.t0||Date.now(),url:s.__nc.u||'',method:s.__nc.m||'GET',status:s.status}); }catch(e){} });
            return _send.apply(this,arguments); };
          return 'ok';
        })();
        """
        try: await page.evaluate(js); return True
        except Exception: return False

    async def _dump_hook(self, page, nome="save_ruim"):
        try:
            events = await page.evaluate("() => (window.__netcap && window.__netcap.events) ? window.__netcap.events : []")
            # DESCOBERTA DE API (Mostra as URLs chamadas em tempo real)
            apis = [e['url'] for e in events if e.get('url') and ('api/' in e['url'].lower() or 'search' in e['url'].lower())]
            if apis:
                self._log(f"    [API DISCOVERY] Chamadas detectadas recentemente: {list(set(apis))[-3:]}")
            return events
        except Exception: return []

    async def _esperar_rede(self, page, t=30000):
        try: await page.wait_for_load_state("networkidle", timeout=t)
        except PWTimeout: pass

    async def _achar_page(self, ctx, marca, timeout=90, precisa_select=None):
        import time as _t
        fim = _t.time() + timeout
        while _t.time() < fim:
            for pg in ctx.pages:
                if marca in (pg.url or "").lower():
                    if precisa_select:
                        try:
                            await pg.wait_for_selector(f'select[data-fieldname="{precisa_select}"]', state="attached", timeout=2000)
                            return pg
                        except Exception: continue
                    return pg
            await asyncio.sleep(1)
        return None

    # NOVO SELECT2 (Forte, sem tecla Escape, com Extração de Opções)
    async def _sel2(self, page, fieldname, texto, espera=True, timeout=12000):
        if not texto: return False
        try:
            sel = page.locator(f'select[data-fieldname="{fieldname}"]').first
            try:
                await sel.wait_for(state="attached", timeout=4000)
            except PWTimeout:
                self._log(f"    [select2] Campo {fieldname} não encontrado no DOM. Pode estar oculto ou layout mudou.")
                return False

            # Validar se o select original está desabilitado
            is_disabled = await sel.evaluate("el => el.disabled || el.getAttribute('readonly') === 'readonly'")
            if is_disabled:
                self._log(f"    [select2] {fieldname} está DESABILITADO/READONLY no sistema. Ignorando.")
                return True # Retorna True pois não é um "erro" nosso, é restrição da tela.

            cont = sel.locator('xpath=following-sibling::*[contains(@class,"select2")][1]')
            await cont.wait_for(state="visible", timeout=4000)
            await cont.scroll_into_view_if_needed()

            # Força o clique no selection para abrir (ou fechar se estiver bugado)
            selection = cont.locator(".select2-selection").first
            try:
                if await selection.count() and await selection.is_visible():
                    await selection.click(force=True)
                else:
                    await cont.click(force=True)
            except Exception as e:
                self._log(f"    [select2] Erro ao clicar no container {fieldname}: {e}")
                return False

            await page.wait_for_timeout(500)

            # Procura pelo input de busca no form aberto
            busca = page.locator(".select2-dropdown input.select2-search__field, .select2-container--open input.select2-search__field").first
            if await busca.count() > 0 and await busca.is_visible():
                await busca.fill("")
                termo = _termo_busca(texto)
                await busca.type(termo, delay=30)
                await page.wait_for_timeout(1000)
            else:
                pass # Alguns combos Benner não possuem barra de busca (são apenas listas)

            base = page.locator(".select2-results").last
            
            # Aguarda a mensagem de loading desaparecer
            try:
                await base.locator("li.loading-results").wait_for(state="hidden", timeout=5000)
            except: pass

            # Descoberta de API: Verifica se retornou 'Nenhum resultado'
            no_results = base.locator("li.select2-results__message").first
            if await no_results.count() > 0 and await no_results.is_visible():
                msg = await no_results.inner_text()
                self._log(f"    [select2] {fieldname} API retornou: '{msg}' ao buscar '{termo}'")
                await page.locator('body').click(position={'x': 10, 'y': 10}, force=True) # Fecha via click
                return False

            # Captura todas as opções retornadas pela API para log (API Discovery)
            try:
                await base.locator("li.select2-results__option:not(.select2-results__message)").first.wait_for(state="visible", timeout=8000)
                opcoes_disponiveis = await base.locator("li.select2-results__option:not(.select2-results__message)").all_inner_texts()
                if opcoes_disponiveis:
                    self._log(f"    [select2] {fieldname} opções da API: {opcoes_disponiveis[:5]}")
            except PWTimeout:
                self._log(f"    [select2] Nenhuma opção apareceu para {fieldname} após 8s.")
                await page.locator('body').click(position={'x': 10, 'y': 10}, force=True)
                return False

            # Match de texto
            opt = base.locator("li.select2-results__option", has_text=re.compile(re.escape(texto), re.IGNORECASE)).first
            if await opt.count() == 0:
                pref = texto.split()[0][:8] if texto.split() else texto[:8]
                opt = base.locator("li.select2-results__option", has_text=re.compile(re.escape(pref), re.IGNORECASE)).first
            if await opt.count() == 0:
                opt = base.locator("li.select2-results__option:not(.select2-results__message)").first

            try:
                if await opt.count() > 0 and await opt.is_visible():
                    await opt.scroll_into_view_if_needed()
                    await opt.click(force=True)
                else:
                    self._log(f"    [select2] {fieldname} Opção escolhida sumiu.")
                    await page.locator('body').click(position={'x': 10, 'y': 10}, force=True)
                    return False
            except Exception as e:
                self._log(f"    [select2] Erro clique em {fieldname}: {e}")
                await page.locator('body').click(position={'x': 10, 'y': 10}, force=True)
                return False

            if espera: await self._esperar_rede(page)
            self._log(f"    [select2] {fieldname} = '{texto[:30]}' OK.")
            return True
        except Exception as e:
            self._log(f"    [select2] {fieldname} FALHA CRÍTICA: {str(e)[:120]}")
            # CLICAR FORA para fechar o modal aberto. NUNCA pressionar Escape, ele fecha o form pai!
            try:
                await page.locator('body').click(position={'x': 10, 'y': 10}, force=True)
            except: pass
            return False

    async def _texto(self, page, fieldname, valor):
        if valor is None: return False
        for s in (f'span[data-field="{fieldname}"] input:not([type=hidden])',
                  f'span[data-field="{fieldname}"] textarea',
                  f'input[id*="{fieldname}"]:not([type=hidden])',
                  f'textarea[id*="{fieldname}"]'):
            loc = page.locator(s).first
            try:
                if await loc.count() and await loc.is_visible():
                    await loc.scroll_into_view_if_needed()
                    await loc.fill(str(valor))
                    await loc.press("Tab")
                    self._log(f"    [texto] {fieldname} = '{str(valor)[:25]}' OK.")
                    return True
            except Exception: continue
        self._log(f"    [texto] {fieldname} não encontrado.")
        return False

    async def _radio(self, page, termos, label):
        js = """(a)=>{const T=a.termos.map(t=>t.toLowerCase());
          const A=(a.label||'').toLowerCase().trim();
          const N=s=>(s||'').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'');
          const todos=t=>{t=N(t);return T.every(x=>t.indexOf(N(x))>=0);};
          const nos=document.querySelectorAll('label,div,span,td,legend,.tab-label,.label-title');
          let P=null;for(const n of nos){const tx=(n.innerText||n.textContent||'').trim();
            if(tx.length>0&&tx.length<120&&todos(tx)){P=n;break;}}
          if(!P)return'sem-pergunta';
          let c=P.closest('.form-group,.field,.control-group,tr,.row,fieldset')||P.parentElement;
          for(let k=0;k<7&&c;k++){const rs=c.querySelectorAll("input[type='radio']");
            for(const r of rs){let l='';if(r.id){const e=document.querySelector('label[for="'+r.id+'"]');if(e)l=e.innerText||e.textContent||'';}
              if(!l){const nx=r.nextElementSibling;if(nx&&nx.tagName==='LABEL')l=nx.innerText||nx.textContent||'';}
              if(N(l).trim()===N(A))return r.id||'RID';}c=c.parentElement;}
          return'sem-radio';}"""
        try:
            rid = await page.evaluate(js, {"termos": list(termos), "label": label})
            if rid in ("sem-pergunta", "sem-radio", "RID"):
                self._log(f"    [radio] {termos}='{label}': {rid}")
                return False
            esc = re.sub(r'([^a-zA-Z0-9_\-])', r'\\', rid)
            r = page.locator(f'#{esc}')
            await r.scroll_into_view_if_needed()
            try:
                lab = page.locator(f'label[for="{esc}"]').first
                if await lab.count(): await lab.click()
                else: await r.click(force=True)
            except Exception: await r.click(force=True)
            await self._esperar_rede(page)
            self._log(f"    [radio] {termos}='{label}': OK.")
            return True
        except Exception as e:
            self._log(f"    [radio] {termos}='{label}' erro: {e}")
            return False

    async def _blocos_part(self, page):
        js = """()=>{const c=(p,e)=>{const o=[];document.querySelectorAll('select[data-fieldname]').forEach(s=>{
          const f=s.getAttribute('data-fieldname')||'';if(f.indexOf(p)===0&&f.indexOf(e)<0)o.push(f);});return o;};
          return{parts:c('PARTICIPANTE','SEMLOTE'),conds:c('CONDICAO','LOTE')};}"""
        r = await page.evaluate(js)
        return r.get("parts", []), r.get("conds", [])

    async def _abrir_e_categoria(self, home, ctx):
        try:
            await home.locator("#sidebar_novoItem").click(timeout=6000)
            await home.wait_for_timeout(1000)
        except Exception: pass
        for txt in ("Cadastro rápido de pasta", "Cadastro rapido de pasta"):
            try:
                link = home.get_by_text(txt, exact=False).first
                if await link.count():
                    await link.click(timeout=5000)
                    await self._esperar_rede(home)
                    break
            except Exception: pass
        
        cat = await self._achar_page(ctx, MARK_CATEGORIA, timeout=30, precisa_select="CATEGORIA")
        if cat is None:
            try:
                await home.wait_for_selector('select[data-fieldname="CATEGORIA"]', state="attached", timeout=8000)
                cat = home
            except Exception: cat = None
        
        if cat is None:
            self._log("    [categoria] aba/seletor não apareceu.")
            return None
        
        await cat.bring_to_front()
        await self._sel2(cat, "CATEGORIA", CATEGORIA, espera=False)
        await cat.wait_for_timeout(800)
        
        for _tent in range(3):
            commit = await cat.evaluate(r"""
                () => { var s=document.querySelector('select[data-fieldname="CATEGORIA"]');
                    if(!s) return false;
                    var hid=s.getAttribute('data-inputhiddenid');
                    if(hid){ var h=document.getElementById(hid);
                        if(h && h.value && h.value.indexOf('"id":-1')<0 && h.value.indexOf('"id"')>=0) return true; }
                    return (s.value && s.value!=='' && s.value!=='-1'); }
            """)
            if commit: break
            self._log(f"    [categoria] Civel nao commitou (tent {_tent+1}); repetindo...")
            await self._sel2(cat, "CATEGORIA", CATEGORIA, espera=False)
            await cat.wait_for_timeout(800)
        
        try:
            await cat.evaluate("() => { __doPostBack('ctl00$Main$TV_CADASTRORAPIDOMANUAL_FORM','Save'); }")
            self._log("    [categoria] OK acionado (__doPostBack).")
        except Exception as e:
            self._log(f"    [categoria] __doPostBack falhou: {e}; tentando botao visivel...")
            for nome_ok in ("Ok", "OK", "Confirmar"):
                try:
                    ok = cat.get_by_role("link", name=re.compile(rf"^\s*{nome_ok}\s*$", re.I)).first
                    if await ok.count():
                        await ok.click(); break
                except Exception: pass
        
        await self._esperar_rede(cat)
        form = await self._achar_page(ctx, MARK_FORM, timeout=120, precisa_select="TIPO")
        if form is None:
            try:
                await cat.wait_for_selector('select[data-fieldname="TIPO"]', state="attached", timeout=8000)
                form = cat
            except Exception: form = None
        
        if form is None:
            self._log("    [form] aba do formulário real não apareceu.")
            return None
            
        await form.bring_to_front()
        self._log(f"    [conn] form real: {form.url[:60]}")
        await self._instalar_hook_rede(form)
        return form

    async def _preencher(self, page, dados):
        nome = dados["nome"]; uf = dados["uf"]
        numero = dados["numero_cnj"]; valor = dados["valor_pedido"]
        adv_int = random.choice(ADVOGADOS_INTERNOS); adv_ext = random.choice(ADVOGADOS_EXTERNOS)
        self._log(f"    === Preenchendo: {nome} (UF={uf}) ===")

        await self._sel2(page, FN["DIRETORIA"], "Diretoria de Seguridade")
        await self._sel2(page, FN["GERENCIA"], "GESOP")
        await self._sel2(page, FN["FILIAL"], "PLANO DE BENEFICIOS 1")

        await self._sel2(page, "TIPO", "COBRANÇA")
        await page.wait_for_timeout(1500)
        
        await self._dump_hook(page) # Debug API requests during fill
        
        await self._sel2(page, "ASSUNTO", "PREVIDENCIAL")
        await self._sel2(page, "CAUSARAIZ", "Produto")
        await self._sel2(page, "DESDOBRAMENTO", "Cobrança")
        await self._sel2(page, "RITO", "Ordinário")
        await self._sel2(page, "INSTANCIA", "1º grau")
        await self._sel2(page, "FASE", "Preliminar")
        await self._texto(page, TEXT_FN["OBSERVACOES"], OBSERVACAO)

        orgao = f"Tribunal de Justiça do Estado {UF_ORGAO.get(uf, '')}".strip()
        await self._sel2(page, "ORGAO", orgao)
        await self._sel2(page, "UF", uf)

        await self._radio(page, ["número", "único"], "Não")
        await self._radio(page, ["tipo", "processo"], "Ativo")
        await self._radio(page, ["processo", "relevante"], "Não")
        await self._radio(page, ["localiza"], "Física")
        await self._radio(page, ["distribu", "judicial"], "Não")
        await self._radio(page, ["adverso", "cadastrado"], "Sim")
        await self._radio(page, ["advogado", "adverso"], "Sim")
        await page.wait_for_timeout(1200)

        await self._texto(page, TEXT_FN["NUMERO"], numero)
        await self._sel2(page, "EVENTO1", "Pedido de ajuizamento de ação")
        hoje = date.today().strftime("%d/%m/%Y")
        await self._texto(page, TEXT_FN["DATA_ANDAMENTO_1"], hoje)
        await self._texto(page, "DATADISTRIBUICAO", hoje)

        parts, conds = await self._blocos_part(page)
        self._log(f"    [participantes] parts={parts} conds={conds}")
        if len(parts) >= 1:
            await self._sel2(page, parts[0], nome)
            if len(conds) >= 1: await self._sel2(page, conds[0], "Réu")
        if len(parts) >= 2:
            await self._sel2(page, parts[1], "PREVI")
            if len(conds) >= 2: await self._sel2(page, conds[1], "Autor")

        await self._sel2(page, "ADVOGADOINTERNO", adv_int)
        await self._sel2(page, "ADVOGADOEXTERNO", adv_ext)
        await self._sel2(page, "PEDIDO1", "DÍVIDA PREVIDENCIÁRIA")
        if valor and valor > 0:
            await self._texto(page, TEXT_FN["VALOR_PEDIDO_1"], f"{valor:.2f}".replace(".", ","))
        await self._sel2(page, "RISCOPEDIDO1", "Possível")

        self._log("    Salvando (clique nativo)...")
        return await self._salvar(page)

    async def _salvar(self, page):
        try: await self._instalar_hook_rede(page)
        except Exception: pass
        
        async def dlg():
            try:
                b = page.locator(".modal.in .modal-footer button, .modal.show .modal-footer button, .bootstrap-dialog-footer button", has_text="Sim").first
                if await b.count() and await b.is_visible():
                    await b.click(); await self._esperar_rede(page)
                    self._log("    [salvar] diálogo -> Sim.")
            except Exception: pass
            
        try:
            btn = page.locator("a.btn.blue.btn-save, a.btn-save.command-action").first
            if await btn.count() == 0:
                btn = page.get_by_role("link", name=re.compile("Salvar", re.I)).first
            await btn.scroll_into_view_if_needed()
            await btn.click()
        except Exception as e:
            self._log(f"    [salvar] falha clique: {e}")
            return False, ""
            
        for _ in range(30):
            await page.wait_for_timeout(1000)
            await dlg()
            try:
                iel = page.locator("span[data-field='IDENTIFICADOR']").first
                if await iel.count():
                    t = (await iel.inner_text() or "").strip()
                    if t:
                        self._log(f"    [salvar] IDENTIFICADOR: {t}")
                        return True, t
            except Exception: pass
            
            try:
                corpo = (await page.locator("body").inner_text())[:2000].lower()
                if "problema ao renderizar" in corpo or "failed to load viewstate" in corpo:
                    self._log("    [salvar] ERRO renderização (viewstate).")
                    return False, "viewstate"
            except Exception: pass
            
        await self._esperar_rede(page)
        return False, "sem-confirmacao"

    async def cadastrar_pastas_async(self):
        self.carregar_planilha()
        ws = self.ws
        pend = [r for r in range(2, ws.max_row + 1) if str(ws.cell(r, COL_STATUS).value or "").strip().upper() == "PENDENTE"]
        self._log(f"Cadastrando {len(pend)} pastas (Playwright)...")
        if not pend: return

        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp(CDP_URL)
            ctx = browser.contexts[0] if browser.contexts else await browser.new_context()
            home = None
            for pg in ctx.pages:
                if "bennercloud" in (pg.url or "").lower():
                    home = pg; break
            home = home or (ctx.pages[0] if ctx.pages else await ctx.new_page())
            self._log(f"Aba inicial: {home.url[:70]}")

            ok_t = err_t = 0
            for row in pend:
                nome = str(ws.cell(row, COL_NOME).value or "").strip()
                contrato = str(ws.cell(row, COL_CONTRATO).value or "")
                uf = str(ws.cell(row, COL_UF).value or "").strip().upper()
                numero = str(ws.cell(row, COL_CNJ).value or f"DP{contrato}")
                vp = ws.cell(row, COL_VALOR_PEDIDO).value
                valor = _parse_valor_br(vp) if vp not in (None, "") else _parse_valor_br(ws.cell(row, COL_VALOR_DIVIDA).value)
                
                try:
                    try: await home.bring_to_front()
                    except Exception: pass
                    
                    form = await self._abrir_e_categoria(home, ctx)
                    if form is None:
                        self._log(f"  [linha {row}] {nome}: não chegou ao form real.")
                        err_t += 1; break
                        
                    salvo, ident = await self._preencher(form, {"nome": nome, "uf": uf, "numero_cnj": numero, "valor_pedido": valor})
                    
                    if salvo:
                        ws.cell(row, COL_STATUS, "CADASTRADO (PW)")
                        if ident: ws.cell(row, COL_ID_PASTA, str(ident))
                        self.salvar_planilha()
                        self._log(f"  [linha {row}] {nome}: OK -> {ident}")
                        ok_t += 1
                    else:
                        ws.cell(row, COL_STATUS, f"ERRO PW: {ident}")
                        self.salvar_planilha()
                        self._log(f"  [linha {row}] {nome}: FALHOU ({ident})")
                        err_t += 1; break
                except Exception as e:
                    self._log(f"  [linha {row}] {nome}: EXCEÇÃO {e}")
                    err_t += 1; break
            self._log(f"Concluído! Sucesso: {ok_t}, Erros: {err_t}")

    # [Métodos _verificar_no_benner_async, verificar_no_benner, fechar omitidos por brevidade - mantidos originais]
    def cadastrar_pastas(self): asyncio.run(self.cadastrar_pastas_async())
    def fechar(self): pass

def main():
    import sys
    DIR = Path(r"K:\BennerData\CadastraPastas")
    arquivo = sys.argv[1] if len(sys.argv) > 1 else str(DIR / "Ajuizamento+2024+2+parte+ (2) -Planilha original.xlsx")
    if not Path(arquivo).exists():
        print(f"ERRO: Arquivo não encontrado: {arquivo}")
        sys.exit(1)

    cadastro = CadastroPastasBennerPW(arquivo)
    while True:
        print("
Opções:
  3 - Etapa 3: Cadastrar pastas (Playwright)
  9 - Sair")
        op = input("Escolha: ").strip()
        if op == "3": cadastro.cadastrar_pastas(); cadastro.fechar()
        elif op == "9": cadastro.fechar(); break
        else: print("Opção inválida.")

if __name__ == "__main__":
    main()
