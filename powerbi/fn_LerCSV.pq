// ══════════════════════════════════════════════════════════
// fn_LerCSV — Função base reutilizável
// ──────────────────────────────────────────────────────────
// COMO USAR:
//   1. Obter Dados → Consulta Nula → Editor Avançado
//   2. Cole este bloco completo
//   3. Nomeie a query como: fn_LerCSV
//   4. Clique direito na query → desmarque "Habilitar Carregamento"
//   5. Fechar e Aplicar
// ══════════════════════════════════════════════════════════

(nomeArquivo as text) =>
let
    Caminho  = "C:\BennerData\" & nomeArquivo & ".csv",
    Fonte    = Csv.Document(
                   File.Contents(Caminho),
                   [
                       Delimiter   = ",",
                       Encoding    = 65001,
                       QuoteStyle  = QuoteStyle.Csv
                   ]
               ),
    Tabela   = Table.PromoteHeaders(Fonte, [PromoteAllScalars = true])
in
    Tabela