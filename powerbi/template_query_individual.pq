// ══════════════════════════════════════════════════════════
// TEMPLATE — Query individual por datasource K_
// ══════════════════════════════════════════════════════════
//
// Crie uma Consulta Nula para cada K_ que quiser usar:
//
// Nome da query: K_RESUMODASPASTAS
// ──────────────────────────────────
// let Tabela = BennerDados[K_RESUMODASPASTAS] in Tabela
//
// Nome da query: K_BASEDEPROCESSOS
// ──────────────────────────────────
// let Tabela = BennerDados[K_BASEDEPROCESSOS] in Tabela
//
// Nome da query: K_BASEDEPASTAS
// ──────────────────────────────────
// let Tabela = BennerDados[K_BASEDEPASTAS] in Tabela
//
// Nome da query: K_BASEDEPEDIDOS
// ──────────────────────────────────
// let Tabela = BennerDados[K_BASEDEPEDIDOS] in Tabela
//
// Nome da query: K_BASEFINANCEIRO
// ──────────────────────────────────
// let Tabela = BennerDados[K_BASEFINANCEIRO] in Tabela
//
// ══════════════════════════════════════════════════════════
// NOVOS K_ ADICIONADOS:
// Basta criar uma nova query com o padrão acima.
// A função detecta o novo CSV automaticamente! ✅
// ══════════════════════════════════════════════════════════

// Exemplo funcional — lista todos os K_ disponíveis na pasta:
let
    Nomes = Record.FieldNames(BennerDados)
in
    Nomes
