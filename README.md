# BENNER - Consultas SQL

Este repositório contém consultas SQL para análise de dados do sistema BENNER.

## Consultas Disponíveis

### 1. Análise de Pagamentos, Depósitos e Provisão

**Arquivo:** `consulta_pagamentos_provisao.sql`

**Objetivo:** Analisar e comparar os valores efetivamente pagos (depósitos + pagamentos) com os valores provisionados para processos jurídicos, identificando divergências e variações percentuais.

**Principais Funcionalidades:**
- Soma de depósitos e pagamentos por pasta (processo)
- Cálculo da diferença absoluta entre valores pagos e provisão
- Cálculo do percentual de variação em relação à provisão
- Classificação por nível de risco (Provável, Possível, Remoto)
- Agrupamento por programa, plano e pedido

**Filtros Aplicados:**
- Processos com valor total de contingência não nulo
- Processos com provisão não nula
- Processos com situação = '1' (ativa)

**Colunas Retornadas:**
- `PASTA`: Identificação da pasta/processo
- `SITUACAO`: Situação do processo
- `TOTAL_VALOR_PAGO`: Soma total de depósitos e pagamentos
- `DIFERENCA_ABSOLUTA`: Diferença entre valor pago e provisão atual
- `PERCENTUAL_VARIACAO`: Percentual de variação (%) em relação à provisão
- `NIVEL_RISCO`: Nível de risco do processo
- `PROGRAMA`: Nome do programa
- `PLANO`: Nome do plano
- `PEDIDO`: Nome de integração do pedido
- `TOTAL_DEPOSITOS`: Total apenas de depósitos
- `TOTAL_PAGAMENTOS`: Total apenas de pagamentos
- `PROVISAO_ATUAL`: Valor da provisão atual

**Ordenação:** Resultados ordenados por diferença absoluta (decrescente)

## Como Utilizar

1. Conecte-se ao banco de dados BENNER
2. Execute a consulta SQL desejada
3. Analise os resultados conforme a necessidade

## Estrutura do Banco de Dados

Consulte o arquivo `Dicionario de Dados.pdf` ou `Dicionario de Dados.txt` para informações detalhadas sobre as tabelas e campos utilizados.

## Tabelas Principais

### Consulta de Pagamentos e Provisão

- **PR_PROCESSOS**: Processos jurídicos
- **K9_PASTAPROGRAMAPLANO**: Relacionamento entre pasta, programa e plano
- **K9_PLANO**: Planos de contingência
- **K9_PROGRAMA**: Programas
- **PR_PROCESSOPEDIDOS**: Relacionamento entre processos e pedidos
- **PR_PEDIDOS**: Pedidos
- **PR_PROCESSODEPOSITOS**: Depósitos realizados nos processos
- **FI_SOLICITACAOPAGAMENTOS**: Solicitações de pagamento
- **PR_PROCESSOPROVISAOVALORES**: Valores de provisão dos processos

## Notas Importantes

- A consulta utiliza `LEFT JOIN` para garantir que processos sem determinados relacionamentos sejam incluídos
- O cálculo do percentual de variação protege contra divisão por zero
- Os valores são agrupados por identificador da pasta, situação, provisão e outros campos relevantes
