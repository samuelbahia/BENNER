# Power BI — Benner Jurídico | Datasources K_ Dinâmicos

## Visão Geral

Esta pasta contém os arquivos Power Query M para conectar o Power BI aos dados extraídos da API Benner Jurídico pelo script `buscar_benner.py`.

A arquitetura usa **Registro Dinâmico**: a função `fn_GerarTabelasDinamicas` detecta automaticamente todos os arquivos `K_*.csv` na pasta `C:\BennerData`, sem necessidade de alterações quando novos datasources forem adicionados.

---

## Pré-requisitos

- `buscar_benner.py` configurado e rodando com sucesso
- CSVs gerados em `C:\BennerData\`
- Power BI Desktop instalado

---

## Arquivos

| Arquivo | Descrição | Carregar? |
|---|---|---|
| `fn_GerarTabelasDinamicas.pq` | Função principal — lê pasta e monta Record dinâmico | ❌ Não |
| `BennerDados.pq` | Instancia a função com o caminho `C:\BennerData` | ❌ Não |
| `template_query_individual.pq` | 41 linhas prontas para criar queries individuais | — |
| `fn_LerCSV.pq` | Função auxiliar alternativa (Opção A) | ❌ Não |
| `queries_k_datasources.pq` | 41 queries usando fn_LerCSV (Opção A alternativa) | — |

---

## Configuração — Passo a Passo

### 1️⃣ Criar `fn_GerarTabelasDinamicas`

```
Power BI → Transformar Dados → Nova Consulta → Consulta Nula
→ Editor Avançado
→ Cole o conteúdo de fn_GerarTabelasDinamicas.pq
→ Nomeie: fn_GerarTabelasDinamicas
→ Clique direito → desmarque "Habilitar Carregamento"
→ Fechar e Aplicar
```

### 2️⃣ Criar `BennerDados`

```
Power BI → Nova Consulta → Consulta Nula
→ Editor Avançado
→ Cole o conteúdo de BennerDados.pq
→ Nomeie: BennerDados
→ Clique direito → desmarque "Habilitar Carregamento"
→ Fechar e Aplicar
```

### 3️⃣ Criar queries individuais para cada K_

Abra `template_query_individual.pq` e copie a linha do K_ desejado:

```
Power BI → Nova Consulta → Consulta Nula
→ Editor Avançado
→ Cole a linha:  let Tabela = BennerDados[K_RESUMODASPASTAS] in Tabela
→ Nomeie:        K_RESUMODASPASTAS
→ Fechar e Aplicar
```

Repita para cada K_ que precisar usar no modelo.

---

## Adicionar Novo K_ no Futuro

```
1. buscar_benner.py  →  adicione o nome em K_DATASOURCES
2. Terminal          →  python buscar_benner.py
3. Power BI          →  Nova Consulta Nula → Editor Avançado:

   let Tabela = BennerDados[K_NOVO_DATASOURCE] in Tabela

4. Nomeie a query:  K_NOVO_DATASOURCE
5. Clique Atualizar ✅
```

> `fn_GerarTabelasDinamicas` e `BennerDados` **não precisam de nenhuma alteração**!

---

## Alterar a Pasta dos CSVs

Se os CSVs estiverem em outra pasta, edite apenas `BennerDados.pq`:

```m
let
    Dados = fn_GerarTabelasDinamicas("D:\OutraPasta\BennerData")
in
    Dados
```

---

## Datasources K_ Disponíveis (41 total)

- K_MODELOESTATISTICOCOMPARATIVOCONDENACOESPROVISOES
- K_PROCESSOSCAPECGEBEN
- K_ID_PAGAMENTOS_LIQUIDACAO_MENSAL
- K_RELATORIOGESOPINADIMPLENCIAFILTROPREVIAUTORA
- K_PROCESSOSPARADOSMAISDE60DIASPREVI
- K_FLUXOSUSPENSOERRO
- K_RESUMOPASTASGESOP
- K_BASEDEBLOQUEIOSPORPLANOEPROGRAMA
- K_DECISOESPREVI
- K_SEGUROSGARANTIA
- K_ACJSPREVIV2025GDP
- K_VALORESPROVISIONADOSPORPLANOEPROGRAMA2024
- K_BASETOTALDEPROCESSOSENCERRADOS2024
- K_BASEDEPEDIDOSPORPLANOEPROGRAMA2024
- K_BASEDEPEDIDOSPORPLANOEPROGRAMA
- K_BASETOTALDEPROCESSOS
- K_VALORESPROVISIONADOSPORPLANOEPROGRAMA
- K_RELATORIOGERAI
- K_BACKTESTGECAT
- K_CONSULTADECPEDPUB
- K_HONORARIOS
- K_TAREFASPREVI
- K_RELATORIOGESOPINADIMPLENCIA
- K_RESUMODASPASTAS
- K_CONSULTASSTATUSTAREFASGECAT
- K_BASEDEPARECERES
- K_USUARIOSATIVOSCOMGRUPO
- K_CONTROLEDELICENCADEUSUARIOS
- K_BASETAREFASPORRESPONSAVEL
- K_BASEDURACAOMEDIAEXECUCAOWFL
- K_BASESLATAREFAS30DIAS
- K_BASESLATAREFAS
- K_BASEPROVISOES
- K_BASEFINANCEIRO
- K_BASEDEPASTAS
- K_BASEDEDECISOES
- K_BASEDEMOVIMENTOSDEDEPOSITOS
- K_BASEDEDEPOSITOS
- K_BASEDEPEDIDOS
- K_BASEDEPARTICIPANTES
- K_BASEDEPROCESSOS

---

## Arquitetura Completa

```
[Agendador de Tarefas Windows]
         ↓ diariamente às 06:00
[buscar_benner.py]
         ↓ gera/atualiza
[C:\BennerData\K_*.csv]
         ↓ lido por
[fn_GerarTabelasDinamicas]
         ↓ instanciada por
[BennerDados]
         ↓ acessado por
[K_RESUMODASPASTAS] [K_BASEDEPROCESSOS] ... (41 tabelas)
         ↓
[Modelo Power BI → Relatórios e Dashboards]
```