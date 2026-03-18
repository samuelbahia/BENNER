// ══════════════════════════════════════════════════════════
// queries_k_datasources.pq
// 41 queries Power Query M — Datasources K_ do Benner Jurídico
// ──────────────────────────────────────────────────────────
// PRÉ-REQUISITO:
//   Criar primeiro a função fn_LerCSV (arquivo powerbi/fn_LerCSV.pq)
//
// COMO USAR:
//   1. Crie fn_LerCSV conforme instruções em fn_LerCSV.pq
//   2. Para cada bloco abaixo:
//        → Obter Dados → Consulta Nula → Editor Avançado
//        → Cole o bloco correspondente
//        → Nomeie a query com o nome exato do datasource
//   3. Após criar todas as queries → Fechar e Aplicar
//   4. Os dados atualizam automaticamente ao clicar "Atualizar"
//      lendo os CSVs gerados pelo buscar_benner.py
//
// PASTA DOS CSVs: C:\BennerData\
// ══════════════════════════════════════════════════════════


// ── [01/41] K_MODELOESTATISTICOCOMPARATIVOCONDENACOESPROVISOES ──
// Nome da query: K_MODELOESTATISTICOCOMPARATIVOCONDENACOESPROVISOES
let Tabela = fn_LerCSV("K_MODELOESTATISTICOCOMPARATIVOCONDENACOESPROVISOES") in Tabela


// ── [02/41] K_PROCESSOSCAPECGEBEN ──
// Nome da query: K_PROCESSOSCAPECGEBEN
let Tabela = fn_LerCSV("K_PROCESSOSCAPECGEBEN") in Tabela


// ── [03/41] K_ID_PAGAMENTOS_LIQUIDACAO_MENSAL ──
// Nome da query: K_ID_PAGAMENTOS_LIQUIDACAO_MENSAL
let Tabela = fn_LerCSV("K_ID_PAGAMENTOS_LIQUIDACAO_MENSAL") in Tabela


// ── [04/41] K_RELATORIOGESOPINADIMPLENCIAFILTROPREVIAUTORA ──
// Nome da query: K_RELATORIOGESOPINADIMPLENCIAFILTROPREVIAUTORA
let Tabela = fn_LerCSV("K_RELATORIOGESOPINADIMPLENCIAFILTROPREVIAUTORA") in Tabela


// ── [05/41] K_PROCESSOSPARADOSMAISDE60DIASPREVI ──
// Nome da query: K_PROCESSOSPARADOSMAISDE60DIASPREVI
let Tabela = fn_LerCSV("K_PROCESSOSPARADOSMAISDE60DIASPREVI") in Tabela


// ── [06/41] K_FLUXOSUSPENSOERRO ──
// Nome da query: K_FLUXOSUSPENSOERRO
let Tabela = fn_LerCSV("K_FLUXOSUSPENSOERRO") in Tabela


// ── [07/41] K_RESUMOPASTASGESOP ──
// Nome da query: K_RESUMOPASTASGESOP
let Tabela = fn_LerCSV("K_RESUMOPASTASGESOP") in Tabela


// ── [08/41] K_BASEDEBLOQUEIOSPORPLANOEPROGRAMA ──
// Nome da query: K_BASEDEBLOQUEIOSPORPLANOEPROGRAMA
let Tabela = fn_LerCSV("K_BASEDEBLOQUEIOSPORPLANOEPROGRAMA") in Tabela


// ── [09/41] K_DECISOESPREVI ──
// Nome da query: K_DECISOESPREVI
let Tabela = fn_LerCSV("K_DECISOESPREVI") in Tabela


// ── [10/41] K_SEGUROSGARANTIA ──
// Nome da query: K_SEGUROSGARANTIA
let Tabela = fn_LerCSV("K_SEGUROSGARANTIA") in Tabela


// ── [11/41] K_ACJSPREVIV2025GDP ──
// Nome da query: K_ACJSPREVIV2025GDP
let Tabela = fn_LerCSV("K_ACJSPREVIV2025GDP") in Tabela


// ── [12/41] K_VALORESPROVISIONADOSPORPLANOEPROGRAMA2024 ──
// Nome da query: K_VALORESPROVISIONADOSPORPLANOEPROGRAMA2024
let Tabela = fn_LerCSV("K_VALORESPROVISIONADOSPORPLANOEPROGRAMA2024") in Tabela


// ── [13/41] K_BASETOTALDEPROCESSOSENCERRADOS2024 ──
// Nome da query: K_BASETOTALDEPROCESSOSENCERRADOS2024
let Tabela = fn_LerCSV("K_BASETOTALDEPROCESSOSENCERRADOS2024") in Tabela


// ── [14/41] K_BASEDEPEDIDOSPORPLANOEPROGRAMA2024 ──
// Nome da query: K_BASEDEPEDIDOSPORPLANOEPROGRAMA2024
let Tabela = fn_LerCSV("K_BASEDEPEDIDOSPORPLANOEPROGRAMA2024") in Tabela


// ── [15/41] K_BASEDEPEDIDOSPORPLANOEPROGRAMA ──
// Nome da query: K_BASEDEPEDIDOSPORPLANOEPROGRAMA
let Tabela = fn_LerCSV("K_BASEDEPEDIDOSPORPLANOEPROGRAMA") in Tabela


// ── [16/41] K_BASETOTALDEPROCESSOS ──
// Nome da query: K_BASETOTALDEPROCESSOS
let Tabela = fn_LerCSV("K_BASETOTALDEPROCESSOS") in Tabela


// ── [17/41] K_VALORESPROVISIONADOSPORPLANOEPROGRAMA ──
// Nome da query: K_VALORESPROVISIONADOSPORPLANOEPROGRAMA
let Tabela = fn_LerCSV("K_VALORESPROVISIONADOSPORPLANOEPROGRAMA") in Tabela


// ── [18/41] K_RELATORIOGERAI ──
// Nome da query: K_RELATORIOGERAI
let Tabela = fn_LerCSV("K_RELATORIOGERAI") in Tabela


// ── [19/41] K_BACKTESTGECAT ──
// Nome da query: K_BACKTESTGECAT
let Tabela = fn_LerCSV("K_BACKTESTGECAT") in Tabela


// ── [20/41] K_CONSULTADECPEDPUB ──
// Nome da query: K_CONSULTADECPEDPUB
let Tabela = fn_LerCSV("K_CONSULTADECPEDPUB") in Tabela


// ── [21/41] K_HONORARIOS ──
// Nome da query: K_HONORARIOS
let Tabela = fn_LerCSV("K_HONORARIOS") in Tabela


// ── [22/41] K_TAREFASPREVI ──
// Nome da query: K_TAREFASPREVI
let Tabela = fn_LerCSV("K_TAREFASPREVI") in Tabela


// ── [23/41] K_RELATORIOGESOPINADIMPLENCIA ──
// Nome da query: K_RELATORIOGESOPINADIMPLENCIA
let Tabela = fn_LerCSV("K_RELATORIOGESOPINADIMPLENCIA") in Tabela


// ── [24/41] K_RESUMODASPASTAS ──
// Nome da query: K_RESUMODASPASTAS
let Tabela = fn_LerCSV("K_RESUMODASPASTAS") in Tabela


// ── [25/41] K_CONSULTASSTATUSTAREFASGECAT ──
// Nome da query: K_CONSULTASSTATUSTAREFASGECAT
let Tabela = fn_LerCSV("K_CONSULTASSTATUSTAREFASGECAT") in Tabela


// ── [26/41] K_BASEDEPARECERES ──
// Nome da query: K_BASEDEPARECERES
let Tabela = fn_LerCSV("K_BASEDEPARECERES") in Tabela


// ── [27/41] K_USUARIOSATIVOSCOMGRUPO ──
// Nome da query: K_USUARIOSATIVOSCOMGRUPO
let Tabela = fn_LerCSV("K_USUARIOSATIVOSCOMGRUPO") in Tabela


// ── [28/41] K_CONTROLEDELICENCADEUSUARIOS ──
// Nome da query: K_CONTROLEDELICENCADEUSUARIOS
let Tabela = fn_LerCSV("K_CONTROLEDELICENCADEUSUARIOS") in Tabela


// ── [29/41] K_BASETAREFASPORRESPONSAVEL ──
// Nome da query: K_BASETAREFASPORRESPONSAVEL
let Tabela = fn_LerCSV("K_BASETAREFASPORRESPONSAVEL") in Tabela


// ── [30/41] K_BASEDURACAOMEDIAEXECUCAOWFL ──
// Nome da query: K_BASEDURACAOMEDIAEXECUCAOWFL
let Tabela = fn_LerCSV("K_BASEDURACAOMEDIAEXECUCAOWFL") in Tabela


// ── [31/41] K_BASESLATAREFAS30DIAS ──
// Nome da query: K_BASESLATAREFAS30DIAS
let Tabela = fn_LerCSV("K_BASESLATAREFAS30DIAS") in Tabela


// ── [32/41] K_BASESLATAREFAS ──
// Nome da query: K_BASESLATAREFAS
let Tabela = fn_LerCSV("K_BASESLATAREFAS") in Tabela


// ── [33/41] K_BASEPROVISOES ──
// Nome da query: K_BASEPROVISOES
let Tabela = fn_LerCSV("K_BASEPROVISOES") in Tabela


// ── [34/41] K_BASEFINANCEIRO ──
// Nome da query: K_BASEFINANCEIRO
let Tabela = fn_LerCSV("K_BASEFINANCEIRO") in Tabela


// ── [35/41] K_BASEDEPASTAS ──
// Nome da query: K_BASEDEPASTAS
let Tabela = fn_LerCSV("K_BASEDEPASTAS") in Tabela


// ── [36/41] K_BASEDEDECISOES ──
// Nome da query: K_BASEDEDECISOES
let Tabela = fn_LerCSV("K_BASEDEDECISOES") in Tabela


// ── [37/41] K_BASEDEMOVIMENTOSDEDEPOSITOS ──
// Nome da query: K_BASEDEMOVIMENTOSDEDEPOSITOS
let Tabela = fn_LerCSV("K_BASEDEMOVIMENTOSDEDEPOSITOS") in Tabela


// ── [38/41] K_BASEDEDEPOSITOS ──
// Nome da query: K_BASEDEDEPOSITOS
let Tabela = fn_LerCSV("K_BASEDEDEPOSITOS") in Tabela


// ── [39/41] K_BASEDEPEDIDOS ──
// Nome da query: K_BASEDEPEDIDOS
let Tabela = fn_LerCSV("K_BASEDEPEDIDOS") in Tabela


// ── [40/41] K_BASEDEPARTICIPANTES ──
// Nome da query: K_BASEDEPARTICIPANTES
let Tabela = fn_LerCSV("K_BASEDEPARTICIPANTES") in Tabela


// ── [41/41] K_BASEDEPROCESSOS ──
// Nome da query: K_BASEDEPROCESSOS
let Tabela = fn_LerCSV("K_BASEDEPROCESSOS") in Tabela