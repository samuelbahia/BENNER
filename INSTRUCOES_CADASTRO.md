# Instruções - Cadastro de Pastas Benner (Inadimplemento)

## Resumo da Análise Prévia

A planilha contém **118 operações**. A análise identificou:

### Duplicatas Exatas (mesmo participante, mesmo contrato, mesmo valor):
| Participante | Contrato | Valor |
|---|---|---|
| ALOISIO BRANDAO VIDIGAL | 61232 | R$ 10.535,26 |
| SERGIO AMAURY MORAES DE ARAUJO | 61992 | R$ 17.607,22 |

**Recomendação:** Remover as linhas duplicadas (2 linhas a menos = 116 cadastros efetivos).

### Mesmo Participante com Operações Distintas:
| Participante | Contratos | Valores |
|---|---|---|
| AVANI MOURA PAJUABA | 61529 / 62778 | R$ 7.210,31 / R$ 11.157,03 |
| ANA MARIA FERNANDES DOS SANTOS PALMA | 62289 / 61412 | R$ 21.701,98 / R$ 11.814,52 |

**Recomendação:** Cadastrar como pastas separadas (contratos distintos), mas verificar se já não existe pasta com o mesmo objeto para o participante.

### Já Cadastrados no Benner (coluna "Benner" = "Parecer"):
1. GENICIA BELARMINO DE AMORIM
2. NEIDE ASSIS
3. SOLANGE MARIA DE SOUZA RIBEIRO
4. FRANCISCA EDLAMAR FERNANDES
5. LEA LENI AZEREDO E MELO

**Recomendação:** Verificar manualmente se a pasta existente tem o mesmo objeto antes de cadastrar nova.

---

## Como Usar o VBA

### Passo 1: Preparar a Planilha
1. Abra o arquivo `.xlsx` no Excel
2. Salve como `.xlsm` (Pasta de Trabalho Habilitada para Macro)
3. Abra o Editor VBA (Alt+F11)
4. Importe o arquivo `VBA_CadastroPastas_Benner.bas` (Arquivo > Importar)
5. Adicione as referências necessárias (Ferramentas > Referências):
   - Microsoft Internet Controls
   - Microsoft HTML Object Library

### Passo 2: Análise Prévia
1. Execute a macro `AnalisePreviaDuplicidades` (Alt+F8)
2. Revise as colunas AC (ANÁLISE DUPLICIDADE) e AD (STATUS CADASTRO)
3. Ajuste manualmente o STATUS para "NÃO CADASTRAR" nas linhas que não devem ser processadas

### Passo 3: Cadastro
1. Faça login no Benner Web antes de executar
2. Execute a macro `CadastrarPastasBenner`
3. Acompanhe o progresso na coluna AD (STATUS CADASTRO)

### Passo 4: Verificação
1. Execute `GerarRelatorioStatus` para ver resumo
2. Verifique linhas com status "ERRO" e trate manualmente

---

## Parâmetros de Cadastro

| Campo | Valor |
|---|---|
| Objeto | DÍVIDA PREVIDENCIÁRIA |
| Chance Êxito | Possível |
| Valor P. Condenação | Conforme planilha (col O) |
| Plano | 1 = Plano 1, 2 = Plano PREVI Futuro |
| Programa | Previdencial |
| Gerência | GESOP |
| Processo | Não distribuído |
| Número CNJ | DP + nº contrato |
| Situação | Baixa Provisória |
| Condução | Recuperação de Créditos |

## Andamento e Providências

Após cadastro, é lançado: **PEDIDO DE AJUIZAMENTO DE AÇÃO**

Providências geradas automaticamente:
1. **PREVI AUTORA – DOCUMENTAÇÃO INICIAL** → GESOP, 10 dias úteis
2. **PROVIDENCIAR AJUIZAMENTO** → Escritório Contratado, 15 dias úteis

---

## IMPORTANTE

O VBA utiliza automação via Internet Explorer/objeto COM. Os IDs dos campos no código (`txtObjeto`, `btnNovaPasta`, etc.) são **placeholders** e devem ser ajustados conforme a estrutura real da página HTML do Benner. Para identificar os IDs corretos:

1. Acesse o sistema Benner no navegador
2. Pressione F12 (DevTools)
3. Inspecione cada campo e anote o `id` ou `name`
4. Atualize o código VBA com os seletores corretos
