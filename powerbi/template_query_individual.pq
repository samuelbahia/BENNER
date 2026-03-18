// ══════════════════════════════════════════════════════════
// TEMPLATE — Query individual por datasource K_
// ──────────────────────────────────────────────────────────
// PRÉ-REQUISITOS:
//   ✅ fn_GerarTabelasDinamicas criada e carregamento desabilitado
//   ✅ BennerDados criada e carregamento desabilitado
//   ✅ buscar_benner.py rodou e gerou os CSVs em C:\BennerData
//
// COMO CRIAR UMA QUERY INDIVIDUAL:
//   1. Obter Dados → Consulta Nula → Editor Avançado
//   2. Cole apenas a linha "let Tabela = ..." do K_ desejado
//   3. Nomeie a query com o nome exato do K_
//   4. Fechar e Aplicar
// ══════════════════════════════════════════════════════════

// ── QUERIES INDIVIDUAIS — copie a linha do K_ desejado ──

// [01/41]
let Tabela = BennerDados[K_MODELOESTATISTICOCOMPARATIVOCONDENACOESPROVISOES] in Tabela

// [02/41]
let Tabela = BennerDados[K_PROCESSOSCAPECGEBEN] in Tabela

// [03/41]
let Tabela = BennerDados[K_ID_PAGAMENTOS_LIQUIDACAO_MENSAL] in Tabela

// [04/41]
let Tabela = BennerDados[K_RELATORIOGESOPINADIMPLENCIAFILTROPREVIAUTORA] in Tabela

// [05/41]
let Tabela = BennerDados[K_PROCESSOSPARADOSMAISDE60DIASPREVI] in Tabela

// [06/41]
let Tabela = BennerDados[K_FLUXOSUSPENSOERRO] in Tabela

// [07/41]
let Tabela = BennerDados[K_RESUMOPASTASGESOP] in Tabela

// [08/41]
let Tabela = BennerDados[K_BASEDEBLOQUEIOSPORPLANOEPROGRAMA] in Tabela

// [09/41]
let Tabela = BennerDados[K_DECISOESPREVI] in Tabela

// [10/41]
let Tabela = BennerDados[K_SEGUROSGARANTIA] in Tabela

// [11/41]
let Tabela = BennerDados[K_ACJSPREVIV2025GDP] in Tabela

// [12/41]
let Tabela = BennerDados[K_VALORESPROVISIONADOSPORPLANOEPROGRAMA2024] in Tabela

// [13/41]
let Tabela = BennerDados[K_BASETOTALDEPROCESSOSENCERRADOS2024] in Tabela

// [14/41]
let Tabela = BennerDados[K_BASEDEPEDIDOSPORPLANOEPROGRAMA2024] in Tabela

// [15/41]
let Tabela = BennerDados[K_BASEDEPEDIDOSPORPLANOEPROGRAMA] in Tabela

// [16/41]
let Tabela = BennerDados[K_BASETOTALDEPROCESSOS] in Tabela

// [17/41]
let Tabela = BennerDados[K_VALORESPROVISIONADOSPORPLANOEPROGRAMA] in Tabela

// [18/41]
let Tabela = BennerDados[K_RELATORIOGERAI] in Tabela

// [19/41]
let Tabela = BennerDados[K_BACKTESTGECAT] in Tabela

// [20/41]
let Tabela = BennerDados[K_CONSULTADECPEDPUB] in Tabela

// [21/41]
let Tabela = BennerDados[K_HONORARIOS] in Tabela

// [22/41]
let Tabela = BennerDados[K_TAREFASPREVI] in Tabela

// [23/41]
let Tabela = BennerDados[K_RELATORIOGESOPINADIMPLENCIA] in Tabela

// [24/41]
let Tabela = BennerDados[K_RESUMODASPASTAS] in Tabela

// [25/41]
let Tabela = BennerDados[K_CONSULTASSTATUSTAREFASGECAT] in Tabela

// [26/41]
let Tabela = BennerDados[K_BASEDEPARECERES] in Tabela

// [27/41]
let Tabela = BennerDados[K_USUARIOSATIVOSCOMGRUPO] in Tabela

// [28/41]
let Tabela = BennerDados[K_CONTROLEDELICENCADEUSUARIOS] in Tabela

// [29/41]
let Tabela = BennerDados[K_BASETAREFASPORRESPONSAVEL] in Tabela

// [30/41]
let Tabela = BennerDados[K_BASEDURACAOMEDIAEXECUCAOWFL] in Tabela

// [31/41]
let Tabela = BennerDados[K_BASESLATAREFAS30DIAS] in Tabela

// [32/41]
let Tabela = BennerDados[K_BASESLATAREFAS] in Tabela

// [33/41]
let Tabela = BennerDados[K_BASEPROVISOES] in Tabela

// [34/41]
let Tabela = BennerDados[K_BASEFINANCEIRO] in Tabela

// [35/41]
let Tabela = BennerDados[K_BASEDEPASTAS] in Tabela

// [36/41]
let Tabela = BennerDados[K_BASEDEDECISOES] in Tabela

// [37/41]
let Tabela = BennerDados[K_BASEDEMOVIMENTOSDEDEPOSITOS] in Tabela

// [38/41]
let Tabela = BennerDados[K_BASEDEDEPOSITOS] in Tabela

// [39/41]
let Tabela = BennerDados[K_BASEDEPEDIDOS] in Tabela

// [40/41]
let Tabela = BennerDados[K_BASEDEPARTICIPANTES] in Tabela

// [41/41]
let Tabela = BennerDados[K_BASEDEPROCESSOS] in Tabela

// ══════════════════════════════════════════════════════════
// ADICIONAR NOVO K_:
//   1. Adicione o nome em buscar_benner.py → K_DATASOURCES
//   2. Rode o script: python buscar_benner.py
//   3. Crie nova Consulta Nula no Power BI:
//        let Tabela = BennerDados[K_NOVO_DATASOURCE] in Tabela
//   4. Clique Atualizar ✅
//   Não é necessário alterar fn_GerarTabelasDinamicas ou BennerDados!