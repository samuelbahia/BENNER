-- =====================================================================================
-- Consulta: Análise de Pagamentos, Depósitos e Provisão por Pasta
-- =====================================================================================
-- Descrição: Esta consulta analisa os valores pagos (depósitos + pagamentos) 
--            comparados com a provisão atual de processos jurídicos.
--            Calcula a diferença absoluta e o percentual de variação entre 
--            o total pago e a provisão.
-- 
-- Tabelas Utilizadas:
--   - PR_PROCESSOS: Processos jurídicos (pastas)
--   - K9_PASTAPROGRAMAPLANO: Relacionamento pasta-programa-plano
--   - K9_PLANO: Planos
--   - K9_PROGRAMA: Programas
--   - PR_PROCESSOPEDIDOS: Relacionamento processo-pedido
--   - PR_PEDIDOS: Pedidos
--   - PR_PROCESSODEPOSITOS: Depósitos do processo
--   - FI_SOLICITACAOPAGAMENTOS: Solicitações de pagamento
--   - PR_PROCESSOPROVISAOVALORES: Valores de provisão do processo
-- 
-- Filtros:
--   - Apenas processos com VALORTOTALCONTINGENCIA não nulo
--   - Apenas processos com provisão não nula
--   - Apenas processos com SITUACAO = '1'
-- 
-- Colunas de Saída:
--   - PASTA: Identificação da pasta
--   - SITUACAO: Situação do processo
--   - TOTAL_VALOR_PAGO: Soma de depósitos e pagamentos
--   - DIFERENCA_ABSOLUTA: Diferença entre valor pago e provisão
--   - PERCENTUAL_VARIACAO: Percentual de variação em relação à provisão
--   - NIVEL_RISCO: Nível de risco (Provável/Possível/Remoto)
--   - PROGRAMA: Nome do programa
--   - PLANO: Nome do plano
--   - PEDIDO: Nome de integração do pedido
--   - TOTAL_DEPOSITOS: Total de depósitos
--   - TOTAL_PAGAMENTOS: Total de pagamentos
--   - PROVISAO_ATUAL: Provisão atual
-- =====================================================================================

SELECT 
    p.IDENTIFICADOR AS PASTA, -- Identificação da Pasta
    p.SITUACAO, -- Situação do Processo
    (COALESCE(SUM(dep.VALOR), 0) + COALESCE(SUM(pagamento.VALORTOTAL), 0)) AS TOTAL_VALOR_PAGO, -- Total de Depósitos e Pagamentos
    (COALESCE(SUM(dep.VALOR), 0) + COALESCE(SUM(pagamento.VALORTOTAL), 0) - provisao.VALORTOTALATUAL) AS DIFERENCA_ABSOLUTA, -- Diferença Absoluta
    CASE 
        WHEN provisao.VALORTOTALATUAL > 0 THEN 
            ROUND(((COALESCE(SUM(dep.VALOR), 0) + COALESCE(SUM(pagamento.VALORTOTAL), 0) - provisao.VALORTOTALATUAL) / provisao.VALORTOTALATUAL) * 100, 2)
        ELSE NULL
    END AS PERCENTUAL_VARIACAO, -- Percentual de Variação
    CASE p.RISCO
        WHEN 1 THEN 'Provável'
        WHEN 2 THEN 'Possível'
        WHEN 3 THEN 'Remoto'
        ELSE 'Não Definido'
    END AS NIVEL_RISCO, -- Risco
    prog.NOME AS PROGRAMA, -- Programa
    plano.NOME AS PLANO, -- Plano
    ped.K9_NOMEINTEGRACAO AS PEDIDO, -- Pedido
    COALESCE(SUM(dep.VALOR), 0) AS TOTAL_DEPOSITOS, -- Total de Depósitos
    COALESCE(SUM(pagamento.VALORTOTAL), 0) AS TOTAL_PAGAMENTOS, -- Total de Pagamentos
    provisao.VALORTOTALATUAL AS PROVISAO_ATUAL -- Provisão Atual
FROM 
    PR_PROCESSOS p
LEFT JOIN K9_PASTAPROGRAMAPLANO ppp ON ppp.PASTA = p.HANDLE
LEFT JOIN K9_PLANO plano ON plano.HANDLE = ppp.PLANO
LEFT JOIN K9_PROGRAMA prog ON prog.HANDLE = plano.PROGRAMA
LEFT JOIN PR_PROCESSOPEDIDOS pp ON pp.PROCESSO = p.HANDLE
LEFT JOIN PR_PEDIDOS ped ON ped.HANDLE = pp.PEDIDO
LEFT JOIN PR_PROCESSODEPOSITOS dep ON dep.PROCESSO = p.HANDLE
LEFT JOIN FI_SOLICITACAOPAGAMENTOS pagamento ON pagamento.PASTA = p.HANDLE -- Relacionamento ajustado
LEFT JOIN PR_PROCESSOPROVISAOVALORES provisao ON provisao.PROCESSO = p.HANDLE
WHERE 
    p.VALORTOTALCONTINGENCIA IS NOT NULL
    AND provisao.VALORTOTALATUAL IS NOT NULL -- Adicionado para evitar casos onde a provisão seja nula
    AND p.SITUACAO = '1' -- Condição para situação específica
GROUP BY 
    p.IDENTIFICADOR, 
    p.SITUACAO, 
    provisao.VALORTOTALATUAL, -- Utilizado na DIFERENCA_ABSOLUTA e PERCENTUAL_VARIACAO
    p.RISCO,
    prog.NOME,
    plano.NOME,
    ped.K9_NOMEINTEGRACAO
ORDER BY DIFERENCA_ABSOLUTA DESC;
