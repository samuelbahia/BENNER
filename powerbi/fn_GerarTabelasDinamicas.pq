// ══════════════════════════════════════════════════════════
// fn_GerarTabelasDinamicas
// ──────────────────────────────────────────────────────────
// Lê todos os CSVs que começam com K_ da pasta informada e
// retorna um Record onde cada campo é o nome do datasource
// (ex: K_RESUMODASPASTAS) e o valor é a tabela correspondente.
//
// Parâmetro:
//   pastaDados  — caminho da pasta onde os CSVs estão salvos
//                 ex: "C:\BennerData"
//
// Uso:
//   fn_GerarTabelasDinamicas("C:\BennerData")
// ══════════════════════════════════════════════════════════

(pastaDados as text) =>
let
    Pasta    = Folder.Files(pastaDados),

    Filtrado = Table.SelectRows(
                   Pasta,
                   each Text.StartsWith([Name], "K_")
                        and Text.EndsWith([Name], ".csv")
               ),

    LerCSV = (conteudo as binary) =>
        let
            Resultado = try
                Table.PromoteHeaders(
                    Csv.Document(
                        conteudo,
                        [Delimiter  = ",",
                         Encoding   = 65001,
                         QuoteStyle = QuoteStyle.Csv]
                    ),
                    [PromoteAllScalars = true]
                )
            otherwise
                #table({}, {})
        in
            Resultado,

    Nomes    = List.Transform(Filtrado[Name], each Text.BeforeDelimiter(_, ".csv")),
    Tabelas  = List.Transform(Filtrado[Content], each LerCSV(_)),
    Registro = Record.FromList(Tabelas, Nomes)
in
    Registro
