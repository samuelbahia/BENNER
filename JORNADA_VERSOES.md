# Jornada de Desenvolvimento - Cadastro de Pastas Benner (Inadimplemento)

Documento que registra todas as versões, erros encontrados e aprimoramentos realizados desde a concepção até a versão final da automação de cadastro de pastas no sistema Benner Jurídico (PREVI).

---

## Visão Geral do Projeto

**Objetivo:** Automatizar o cadastro de 118 operações de cobrança judicial (Dívida Previdenciária) no sistema Benner Jurídico da PREVI, a partir de uma planilha Excel.

**Ferramentas desenvolvidas:**
- VBA (Excel + Internet Explorer COM) — `VBA_CadastroPastas_Benner.bas`
- Python/Selenium — `cadastro_pastas_benner.py`

**Fluxo de 3 Etapas:**
1. **Etapa 1** — Análise prévia local (duplicatas, agrupamentos)
2. **Etapa 2** — Verificação online no Benner (pesquisa de participantes)
3. **Etapa 3** — Cadastro automático via +Novo > Cadastro rápido de pasta > Categoria Cível

---

## Versão 1 — Estrutura Inicial e Upload de Dados
**Commit:** `458798b` — *Add files via upload*

### O que foi feito
- Upload da planilha original (`Ajuizamento+2024+2+parte+ (2) -Planilha original.xlsx`) com 118 operações
- Upload do dicionário de dados (`K_DICIONARIODEDADOS.xlsx`) para referência dos campos do sistema Benner
- Upload do passo a passo de pesquisa no Benner (`Passo a passo para pesquisar o nome e a pasta.zip`)

### Estrutura da planilha identificada
| Coluna | Campo |
|--------|-------|
| A (1) | PLANO ATUAL |
| D (4) | NOME |
| F (6) | CONTRATO |
| O (15) | VAL DIV ATUAL.APOS AMORT. |
| Q (17) | GERÊNCIA |
| T (20) | UF |
| W (23) | CPF |
| AB (28) | Benner (status manual) |

---

## Versão 2 — Macro VBA Inicial com Análise de Duplicatas
**Commit:** `7abf1f5` — *Add VBA macro for Benner folder registration and pre-analysis of duplicates*

### O que foi feito
- Criação do módulo VBA `modCadastroPastas`
- **Etapa 1 (AnalisePreviaDuplicidades):** análise local da planilha
- Identificação de duplicatas exatas e participantes com múltiplas operações
- Criação de colunas auxiliares: ANÁLISE DUPLICIDADE (AC), STATUS CADASTRO (AD), NÚMERO CNJ (AE), PLANO DESCRIÇÃO (AF)
- Criação do `INSTRUCOES_CADASTRO.md` com documentação

### Análise identificada
- **2 duplicatas exatas** (mesmo participante, contrato e valor): ALOISIO BRANDAO VIDIGAL, SERGIO AMAURY MORAES DE ARAUJO
- **2 participantes com operações distintas** (contratos diferentes): AVANI MOURA PAJUABA, ANA MARIA FERNANDES DOS SANTOS PALMA
- **5 já cadastrados** (coluna Benner = "Parecer"): GENICIA BELARMINO DE AMORIM, NEIDE ASSIS, SOLANGE MARIA DE SOUZA RIBEIRO, FRANCISCA EDLAMAR FERNANDES, LEA LENI AZEREDO E MELO

---

## Versão 3 — Pesquisa Online e Fluxo de Cadastro Rápido
**Commit:** `f22d696` — *Enhance VBA with Benner web search pre-check (Pastas > Parte Pasta) and Cadastro Rápido flow*

### O que foi feito
- **Etapa 2 (VerificarNoBenner):** pesquisa online via Pastas > Parte Pasta
- Navega ao menu Pastas, preenche campo "Parte Pasta" com o nome, pesquisa
- Lê resultados e identifica se já existe pasta com mesmo objeto
- **Etapa 3 (CadastrarPastasBenner):** cadastro via +Novo > Cadastro rápido de pasta
- Registra resultados na coluna PESQUISA BENNER (AG)

### Limitações desta versão
- IDs dos campos HTML eram placeholders genéricos (`txtObjeto`, `btnNovaPasta`)
- Necessitava ajuste manual dos seletores conforme estrutura real da página

---

## Versão 4 — Formulário Cível Completo com Participantes e Advogados
**Commit:** `e7b5275` — *Rewrite VBA with complete Cível form fields, participant handling, random lawyers, and pasta ID capture*

### O que foi feito
- Mapeamento completo dos campos do formulário Cível após seleção de categoria
- Preenchimento de: Filial, Gerência, Tipo, Causa de Pedir, Causa Raiz, Processo, Órgão, UF
- Informações de distribuição (data, tipo documento, número CNJ)
- Cadastro de participantes: Adverso (participante) + PREVI (como parte)
- **Sorteio aleatório de advogados** (interno e externo) a partir de listas pré-definidas
- Preenchimento do Pedido (DÍVIDA PREVIDENCIÁRIA) e valor
- Captura do ID da pasta cadastrada para registro na planilha (coluna AH)
- Limpeza da grid de documentos gerada automaticamente

---

## Versão 5 — Campos Rito e Tipo Processo
**Commit:** `5d05675` — *Add Rito (Ordinário) and Tipo Processo (Ativo) fields to Cível form*

### O que foi feito
- Adição do campo **Rito** = "Ordinário"
- Adição do campo **Tipo Processo** = "Ativo" (radio button)
- Constantes adicionadas ao código VBA

---

## Versão 6 — IDs Reais dos Campos ASP.NET
**Commit:** `4231bdf` — *Rewrite VBA to use exact ASP.NET field IDs from Mapa de Campos*

### O que foi feito
- Substituição de todos os placeholders por IDs reais mapeados do sistema Benner
- Prefixo comum: `ctl00_Main_WIDGET_CADASTRO_RAPIDO_PageControl_GERAL_GERAL_`
- Mapeamento completo de 20+ campos com IDs de controle visível e campo VALUE oculto

### Campos mapeados
| Campo | ID (sufixo) |
|-------|-------------|
| Filial | ctl11_FILIAL_VALUE |
| Gerência | ctl22_DIVISAO_VALUE |
| Causa de Pedir | ctl34_ASSUNTO_VALUE |
| Causa Raiz | ctl43_CAUSARAIZ_VALUE |
| Tipo Processo | GroupRadioButton_TIPOPROCESSO_1 |
| Processo | ctl79_DESDOBRAMENTO_VALUE |
| Rito | ctl87_RITO_VALUE |
| Órgão | ctl95_ORGAO_VALUE |
| UF | ctl99_UF_VALUE |

### Erro resolvido
- **Problema:** IDs placeholders não encontravam os campos na página real
- **Solução:** Uso do dicionário de dados (K_DICIONARIODEDADOS.xlsx, aba "Mapa de Campos") para mapear IDs exatos

---

## Versão 7 — Versão Python/Selenium
**Commit:** `708cf51` — *Add Python/Selenium version of Benner folder registration automation*

### O que foi feito
- Criação do `cadastro_pastas_benner.py` como alternativa ao VBA
- Mesma lógica de 3 etapas portada para Python com Selenium WebDriver
- Vantagem: não depende de Internet Explorer (usa Chrome/Edge)
- Classe `CadastroPastasBenner` com métodos para cada etapa
- Uso de `WebDriverWait` e `Expected Conditions` para sincronização

---

## Versão 8 — Correção de Compilação VBA
**Commit:** `cedbcd2` — *Fix VBA compile error: replace Const concatenation with literal strings*

### Erro encontrado
- **Erro:** VBA não permite concatenação em declarações `Const` (ex: `Const X = PFX & "sufixo"`)
- **Mensagem:** Erro de compilação — expressão constante obrigatória

### Correção
- Substituição de todas as constantes concatenadas por strings literais completas

---

## Versão 9 — Consistência de Escritório Externo por Participante
**Commit:** `59a409f` — *Ensure same participant always gets same external law firm across multiple processes*

### O que foi feito
- **Regra de negócio:** Mesmo participante com múltiplos processos → mesmo escritório externo
- Implementação de dicionário/mapa `escritorio_por_participante` que armazena o escritório sorteado na primeira ocorrência
- Aplicado tanto no VBA quanto no Python

---

## Versão 10 — Agrupamento de Participantes com Contratos Múltiplos
**Commit:** `e3cb4ad` — *Group same participant with different contracts into single folder with combined number DP+contracts*

### O que foi feito
- **Regra de negócio:** Mesmo participante com contratos diferentes → uma única pasta
- Número CNJ combinado: `DP{contrato1}/{contrato2}` (ex: `DP61529/62778`)
- Valor do pedido = soma dos valores de todas as operações do participante
- Agrupamento via dicionário `participante_linhas` que mapeia nome → lista de linhas

---

## Versão 11 — Verificação Específica de "Dívida Previdenciária" e ID da Pasta
**Commit:** `ff63e9c` — *Only mark as JÁ CADASTRADO when Dívida Previdenciária found, include folder ID for verification*

### Erro/Problema encontrado
- **Problema:** O sistema marcava como "JÁ CADASTRADO" qualquer participante encontrado no Benner, mesmo se a pasta existente fosse de outro objeto
- **Problema:** Não capturava o ID da pasta para verificação manual

### Correção
- Só marca "JÁ CADASTRADO NO BENNER" quando a pasta existente tem especificamente "DÍVIDA PREVIDENCIÁRIA" como objeto
- Captura o ID da pasta via link `href` (parâmetro `id=`) e registra na coluna ID PASTA
- Formato do resultado: `[NomePasta] ENCONTRADA - MESMO OBJETO (DÍVIDA PREVIDENCIÁRIA) | PASTA:12345`

---

## Versão 12 — Valor Pedido (Soma) e Risco "Possível"
**Commit:** `9db16ff` — *Add valor pedido (summed for grouped contracts) and risco Possível to both Python and VBA*

### O que foi feito
- **Valor Pedido:** coluna VAL DIV ATUAL (O) somada para participantes agrupados
- Nova coluna VALOR PEDIDO (AI/35) na planilha
- **Risco/Chance de Êxito:** definido como "Possível" para todos os cadastros
- Aplicado em ambas as versões (VBA e Python)

---

## Versão 13 — Captura do Nome da Pasta nos Resultados
**Commit:** `85443eb` — *Include Pasta field value from search results in PESQUISA BENNER column*

### O que foi feito
- Captura do valor da primeira célula da linha encontrada (nome/número da pasta)
- Incluído como prefixo no resultado: `[NomeDaPasta] ENCONTRADA - ...`
- Melhora rastreabilidade para verificação manual

---

## Versão 14 — Verificação Específica da Coluna Pedido
**Commit:** `a3d5425` — *Check Pedido column specifically (not full row text) for DÍVIDA PREVIDENCIÁRIA in search results*

### Erro encontrado
- **Problema:** A busca por "DÍVIDA PREVIDENCIÁRIA" era feita no texto completo da linha (`innerText`), gerando falsos positivos quando o texto aparecia em outras colunas
- **Exemplo:** Um participante com "Dívida Previdenciária" no nome da pasta mas com pedido diferente era marcado incorretamente

### Correção
- Verificação específica na segunda célula (`cells[1]`) da tabela de resultados, que corresponde à coluna Pedido
- Comparação case-insensitive com acento e sem acento

---

## Versão 15 — Debug do Menu +Novo (Cadastro Rápido)
**Commit:** `05a0983` — *Add extra wait, more tag searches, and debug MsgBox for Cadastro rápido menu*

### Erro encontrado
- **Erro:** `ERRO: Cadastro rápido não encontrado` ao tentar abrir o submenu +Novo
- **Causa:** O submenu não renderizava a tempo, e a busca não cobria todas as tags HTML possíveis

### Correção temporária
- Adição de `Application.Wait` extra (3 segundos) após clicar em +Novo
- Busca ampliada em mais tags: A, SPAN, LI, DIV, BUTTON
- Adição de `MsgBox doc.body.innerText` para debug (ver conteúdo visível da página)

---

## Versão 16 — Navegação Correta do Sidebar (+Novo)
**Commit:** `663dd7c` — *Fix sidebar menu navigation: use getElementById for sidebar_novoItem, add JS fallback for Cadastro rápido*

### Erro encontrado
- **Problema:** Mesmo com espera extra, o botão "+Novo" não era encontrado de forma confiável
- **Causa raiz:** O botão tem ID fixo `sidebar_novoItem` mas a busca por texto não o localizava

### Correção definitiva
- Uso de `getElementById("sidebar_novoItem")` para localização direta do botão +Novo
- Fallback via JavaScript: `Benner.Page.commandExecute('PR_CADASTRORAPIDOPASTA.FORM/INSERT_CADASTRO_RAPIDO')` para abrir o Cadastro rápido diretamente caso o menu não responda
- Remoção do MsgBox de debug

---

## Versão 17 — Caminho Padrão do Script Python
**Commit:** `0f43730` — *Set default spreadsheet path to K:\BennerData\CadastraPastas in Python script*

### Solicitação
- Definir `K:\BennerData\CadastraPastas` como diretório padrão para localização da planilha e execução do script

### Erro encontrado ao executar
- **Erro:** `python: can't open file 'cadastro_pastas_benner.py'`
- **Causa:** Usuário executou o comando de outro diretório
- **Solução:** Orientação para executar `cd /d K:\BennerData\CadastraPastas` antes de rodar o script

---

## Versão 18 — Campo Parte Pasta como Widget Select2
**Commit:** `9968f27` — *Fix Etapa 2: use select2 widget for Parte Pasta field instead of regular input*

### Erro encontrado
- **Erro:** `ERRO: Campo não encontrado` na Etapa 2 ao tentar preencher o campo "Parte Pasta"
- **Causa:** O campo não é um input comum — é um widget **Select2** (componente JavaScript customizado)

### Correção
- Identificação do widget via `select[@data-fieldname='PARTEPASTA']`
- Nova sequência de interação:
  1. Clicar no `span.select2-selection` para abrir o dropdown
  2. Digitar no `input.select2-search__field` para filtrar
  3. Selecionar a opção da lista `li.select2-results__option`
  4. Clicar em `FilterButton` para executar a pesquisa
- Aplicado no Python (`_pesquisar_parte_pasta`)

---

## Versão 19 (Final) — Etapa 2 via Atalhos > Pessoas > CPF
**Commit:** `b7b7eb8` — *Rewrite VBA Etapa 2: replace PesquisarPartePasta with PesquisarPessoaPorCPF using Atalhos > Pessoas*

### Mudança de abordagem
- **Antes:** Etapa 2 pesquisava por nome em Pastas > Parte Pasta
- **Depois:** Etapa 2 pesquisa por CPF em Atalhos > Pessoas

### Motivação
- A pesquisa por Parte Pasta tinha problemas recorrentes com o widget Select2
- A pesquisa por CPF é mais precisa (identificador único) e mais confiável
- O caminho Atalhos > Pessoas permite verificar diretamente os processos vinculados à pessoa

### O que foi feito
- **VBA:** Substituição das funções `PesquisarPartePasta` e `LerResultadosPesquisa` pela nova `PesquisarPessoaPorCPF`
- **Python:** Substituição de `_pesquisar_parte_pasta` por `_pesquisar_pessoa_por_cpf`
- Adição da constante `URL_PESSOAS` como fallback de navegação
- Novo fluxo:
  1. Navegar para Atalhos > Pessoas
  2. Preencher campo CPF com valor da planilha (coluna W)
  3. Clicar em FilterButton para pesquisar
  4. Se pessoa não encontrada → "PESSOA NÃO ENCONTRADA - OK para cadastrar"
  5. Se encontrada → clicar na pessoa, abrir aba Processos
  6. Verificar se há "Dívida Previdenciária" nos processos
  7. Retornar resultado com ID da pasta se encontrado
  8. Navegar de volta para próxima pesquisa

### Possíveis resultados da Etapa 2
| Resultado | Significado |
|-----------|-------------|
| PESSOA NÃO ENCONTRADA - OK para cadastrar | CPF não existe no Benner, pode cadastrar |
| PESSOA ENCONTRADA - SEM PROCESSOS | Pessoa existe mas sem processos vinculados |
| PESSOA ENCONTRADA - PROCESSOS SEM DÍVIDA PREVIDENCIÁRIA | Tem processos, mas nenhum de Dívida Previdenciária |
| [Pasta] ENCONTRADA - MESMO OBJETO (DÍVIDA PREVIDENCIÁRIA) \| PASTA:ID | Já existe pasta com mesmo objeto — marcar JÁ CADASTRADO |

---

## Resumo da Evolução

| # | Versão | Tipo | Descrição |
|---|--------|------|-----------|
| 1 | Upload inicial | Base | Planilha e dados de referência |
| 2 | VBA básico | Funcionalidade | Análise de duplicatas e estrutura de 3 etapas |
| 3 | Pesquisa online | Funcionalidade | Etapa 2 (Parte Pasta) e Etapa 3 (Cadastro Rápido) |
| 4 | Formulário completo | Funcionalidade | Campos Cível, participantes, advogados, captura ID |
| 5 | Rito e Tipo Processo | Aprimoramento | Campos adicionais no formulário |
| 6 | IDs reais ASP.NET | Correção | Substituição de placeholders por IDs mapeados |
| 7 | Versão Python | Funcionalidade | Alternativa ao VBA com Selenium |
| 8 | Correção compilação | Correção | Const concatenation → strings literais |
| 9 | Escritório consistente | Regra de negócio | Mesmo participante → mesmo escritório |
| 10 | Agrupamento | Regra de negócio | Contratos múltiplos → pasta única, valores somados |
| 11 | Verificação objeto | Correção | Só "JÁ CADASTRADO" se Dívida Previdenciária |
| 12 | Valor Pedido + Risco | Regra de negócio | Soma de valores e risco "Possível" |
| 13 | Nome da pasta | Aprimoramento | Captura do nome da pasta nos resultados |
| 14 | Coluna Pedido | Correção | Verificação específica da coluna Pedido |
| 15 | Debug menu | Investigação | MsgBox e espera extra para +Novo |
| 16 | Sidebar fix | Correção | getElementById + JS fallback para +Novo |
| 17 | Caminho padrão | Aprimoramento | Diretório K:\BennerData\CadastraPastas |
| 18 | Select2 widget | Correção | Campo Parte Pasta como Select2 |
| 19 | CPF via Pessoas | Redesign | Etapa 2 reescrita: Atalhos > Pessoas > CPF |

---

## Arquivos Finais

| Arquivo | Descrição |
|---------|-----------|
| `VBA_CadastroPastas_Benner.bas` | Módulo VBA completo (3 etapas) |
| `cadastro_pastas_benner.py` | Script Python/Selenium equivalente |
| `INSTRUCOES_CADASTRO.md` | Documentação de uso e parâmetros |
| `JORNADA_VERSOES.md` | Este documento |

---

## Lições Aprendidas

1. **Campos ASP.NET WebForms** possuem IDs longos e compostos — o mapeamento prévio via inspeção do HTML é essencial
2. **Widgets Select2** requerem sequência específica de interação (click → type → select) diferente de inputs comuns
3. **Pesquisa por CPF** é mais confiável que por nome para verificação de cadastros existentes
4. **Sidebar do Benner** tem IDs fixos (`sidebar_novoItem`) e aceita comandos JavaScript diretos (`Benner.Page.commandExecute`)
5. **Regras de agrupamento** (mesmo participante → mesma pasta, mesmo escritório) devem ser implementadas desde o início para evitar retrabalho
6. **Testes incrementais** com MsgBox/debug são essenciais quando se automatiza interfaces web complexas
