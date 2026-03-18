# Power BI — Integração Dinâmica com Benner Jurídico

Documentação da solução **Opção C — Registro Dinâmico** para leitura automática dos datasources K_ no Power BI.

---

## Pré-requisitos

- Python 3.8+ instalado com os pacotes `requests` e `pandas`
- Script `buscar_benner.py` configurado com usuário, senha e URL da API Benner
- CSVs gerados em `C:\BennerData` pelo script Python
- Power BI Desktop instalado

---

## Como funciona

```
[buscar_benner.py]  →  C:\BennerData\K_*.csv  →  [Power BI Desktop]
  (roda no terminal       (arquivos locais)         (lê automaticamente
   ou agendador)                                     todos os K_)
```

A função `fn_GerarTabelasDinamicas` lê a pasta dinamicamente — qualquer novo CSV com prefixo `K_` é detectado automaticamente sem alteração no Power BI.

---

## Passo a passo de configuração no Power BI Desktop

### 1. Criar a função `fn_GerarTabelasDinamicas`

1. Abrir Power BI Desktop
2. Ir em **Página Inicial → Transformar dados** (abre o Power Query Editor)
3. Clicar em **Nova Fonte → Consulta Nula**
4. Na barra de fórmulas, colar o conteúdo de `powerbi/fn_GerarTabelasDinamicas.pq`
5. Renomear a query para `fn_GerarTabelasDinamicas`
6. Clicar com o botão direito → **Desabilitar carregamento** ✅

### 2. Criar a query `BennerDados`

1. Clicar em **Nova Fonte → Consulta Nula**
2. Na barra de fórmulas, colar o conteúdo de `powerbi/BennerDados.pq`
3. Renomear a query para `BennerDados`
4. Clicar com o botão direito → **Desabilitar carregamento** ✅

### 3. Criar queries individuais para cada K_

Para cada datasource que quiser usar no relatório:

1. Clicar em **Nova Fonte → Consulta Nula**
2. Digitar (substituindo pelo nome real do K_):
   ```m
   let Tabela = BennerDados[K_RESUMODASPASTAS] in Tabela
   ```
3. Renomear a query com o nome do datasource (ex: `K_RESUMODASPASTAS`)
4. **Não** desabilitar carregamento — essa query deve carregar os dados

---

## Como adicionar um novo datasource K_

1. Adicionar o nome do novo datasource à lista `K_DATASOURCES` em `buscar_benner.py`
2. Rodar o script Python para gerar o CSV:
   ```bash
   python buscar_benner.py
   ```
3. No Power BI, criar uma nova **Consulta Nula**:
   ```m
   let Tabela = BennerDados[K_NOVO_DATASOURCE] in Tabela
   ```
4. Clicar em **Atualizar** — a nova tabela estará disponível ✅

Não é necessário alterar `fn_GerarTabelasDinamicas` nem `BennerDados`.

---

## Atualização de dados

Após rodar o `buscar_benner.py` (que atualiza os CSVs), basta clicar em:

**Power BI Desktop → Página Inicial → Atualizar**

Para automatizar, configure:
- **Agendador de Tarefas do Windows** para rodar o script Python diariamente
- **Power BI Service**: agendar atualização do dataset após o horário do script

---

## Configuração do caminho

O caminho padrão é `C:\BennerData`. Para alterar:

**Em `powerbi/BennerDados.pq`**, troque a string:
```m
let
    Dados = fn_GerarTabelasDinamicas("D:\MinhaPasta\BennerData")
in
    Dados
```

Ou, para tornar configurável via parâmetro no Power BI:
1. Criar um **Parâmetro** chamado `CaminhoBenner` do tipo Texto
2. Alterar `BennerDados` para:
   ```m
   let
       Dados = fn_GerarTabelasDinamicas(CaminhoBenner)
   in
       Dados
   ```

---

## 41 Datasources K_ disponíveis

- `K_MODELOESTATISTICOCOMPARATIVOCONDENACOESPROVISOES`
- `K_PROCESSOSCAPECGEBEN`
- `K_ID_PAGAMENTOS_LIQUIDACAO_MENSAL`
- `K_RELATORIOGESOPINADIMPLENCIAFILTROPREVIAUTORA`
- `K_PROCESSOSPARADOSMAISDE60DIASPREVI`
- `K_FLUXOSUSPENSOERRO`
- `K_RESUMOPASTASGESOP`
- `K_BASEDEBLOQUEIOSPORPLANOEPROGRAMA`
- `K_DECISOESPREVI`
- `K_SEGUROSGARANTIA`
- `K_ACJSPREVIV2025GDP`
- `K_VALORESPROVISIONADOSPORPLANOEPROGRAMA2024`
- `K_BASETOTALDEPROCESSOSENCERRADOS2024`
- `K_BASEDEPEDIDOSPORPLANOEPROGRAMA2024`
- `K_BASEDEPEDIDOSPORPLANOEPROGRAMA`
- `K_BASETOTALDEPROCESSOS`
- `K_VALORESPROVISIONADOSPORPLANOEPROGRAMA`
- `K_RELATORIOGERAI`
- `K_BACKTESTGECAT`
- `K_CONSULTADECPEDPUB`
- `K_HONORARIOS`
- `K_TAREFASPREVI`
- `K_RELATORIOGESOPINADIMPLENCIA`
- `K_RESUMODASPASTAS`
- `K_CONSULTASSTATUSTAREFASGECAT`
- `K_BASEDEPARECERES`
- `K_USUARIOSATIVOSCOMGRUPO`
- `K_CONTROLEDELICENCADEUSUARIOS`
- `K_BASETAREFASPORRESPONSAVEL`
- `K_BASEDURACAOMEDIAEXECUCAOWFL`
- `K_BASESLATAREFAS30DIAS`
- `K_BASESLATAREFAS`
- `K_BASEPROVISOES`
- `K_BASEFINANCEIRO`
- `K_BASEDEPASTAS`
- `K_BASEDEDECISOES`
- `K_BASEDEMOVIMENTOSDEDEPOSITOS`
- `K_BASEDEDEPOSITOS`
- `K_BASEDEPEDIDOS`
- `K_BASEDEPARTICIPANTES`
- `K_BASEDEPROCESSOS`

---

## Estrutura de arquivos

```
BENNER/
├── buscar_benner.py                      ← Script Python de extração
└── powerbi/
    ├── fn_GerarTabelasDinamicas.pq       ← Função Power Query M
    ├── BennerDados.pq                    ← Query principal (não carregar)
    ├── template_query_individual.pq      ← Template para queries individuais
    └── README.md                         ← Esta documentação
```
