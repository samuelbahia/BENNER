// ══════════════════════════════════════════════════════════
// BennerDados
// ──────────────────────────────────────────────────────────
// Instancia fn_GerarTabelasDinamicas com o caminho padrão
// dos CSVs gerados pelo buscar_benner.py.
//
// ⚠️  Marcar como "Não carregar" (Desabilitar carregamento)
//     Esta query serve apenas como base para as individuais.
//
// Para alterar o caminho, edite a string abaixo:
// ══════════════════════════════════════════════════════════

let
    Dados = fn_GerarTabelasDinamicas("C:\BennerData")
in
    Dados
