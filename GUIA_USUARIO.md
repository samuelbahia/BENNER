# Guia do Usuário - SQL Builder Agent

## Visão Geral

O SQL Builder Agent é uma ferramenta inteligente para construir consultas SQL de forma visual e intuitiva. Ele permite:

- ✅ Seleção visual de tabelas e colunas
- ✅ Configuração de JOINs (INNER, LEFT, RIGHT, FULL OUTER)
- ✅ Adição de cláusulas WHERE, ORDER BY, GROUP BY e LIMIT
- ✅ Geração automática de SQL otimizado
- ✅ Interface web moderna e responsiva

## Instalação

### Requisitos
- Python 3.7 ou superior
- pip (instalador de pacotes Python)

### Passos de Instalação

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/samuelbahia/BENNER.git
   cd BENNER
   ```

2. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Inicie o servidor:**
   ```bash
   python app.py
   ```

4. **Acesse a aplicação:**
   Abra seu navegador e acesse: `http://localhost:5000`

## Usando a Interface Web

### 1. Selecionando Tabelas e Colunas

1. No painel **"Selecionar Tabelas e Colunas"**, escolha uma tabela do menu dropdown
2. As colunas disponíveis aparecerão na lista abaixo
3. Clique no botão **"Adicionar"** ao lado de cada coluna que deseja incluir
4. As colunas selecionadas aparecem na seção **"Colunas Selecionadas"**
5. Use o botão **"✕"** para remover qualquer coluna selecionada

**Dica:** Você pode selecionar colunas de múltiplas tabelas para criar consultas com JOINs.

### 2. Configurando JOINs

Para conectar tabelas relacionadas:

1. Clique no botão **"+ Adicionar Join"** no painel de JOINs
2. Configure cada JOIN especificando:
   - **Tipo de Join:** INNER, LEFT, RIGHT ou FULL OUTER
   - **Tabela:** A tabela a ser juntada
   - **Tabela Esquerda:** Primeira tabela da relação
   - **Coluna Esquerda:** Coluna da tabela esquerda (geralmente a chave primária)
   - **Tabela Direita:** Segunda tabela da relação
   - **Coluna Direita:** Coluna da tabela direita (geralmente a chave estrangeira)

**Exemplo de JOIN:**
- Tipo: INNER JOIN
- Tabela: Z_GRUPOUSUARIOS
- Esquerda: PR_PROCESSOS.USUARIO
- Direita: Z_GRUPOUSUARIOS.HANDLE

### 3. Adicionando Filtros e Condições

No painel **"Opções Adicionais"**:

#### WHERE (Filtros)
Digite uma condição por linha. Exemplos:
```sql
PR_PROCESSOS.STATUS = 'ATIVO'
PR_PROCESSOS.VALOR > 1000
Z_GRUPOUSUARIOS.NOME LIKE '%Silva%'
```

#### ORDER BY (Ordenação)
Digite as colunas e direção separados por vírgula:
```
NOME ASC, DATA DESC
```

#### GROUP BY (Agrupamento)
Digite as colunas separadas por vírgula:
```
DEPARTAMENTO, CATEGORIA
```

#### LIMIT (Limitar Resultados)
Digite um número para limitar quantos registros retornar:
```
100
```

### 4. Gerando o SQL

1. Após configurar sua consulta, clique no botão **"🚀 Gerar SQL"**
2. O SQL gerado aparecerá no painel **"SQL Gerado"**
3. Use o botão **"📋 Copiar SQL"** para copiar a consulta
4. Use o botão **"🔄 Resetar Tudo"** para começar uma nova consulta

## Exemplos Práticos

### Exemplo 1: Consulta Simples

**Objetivo:** Listar todos os usuários cujo nome contém "Silva"

**Passos:**
1. Selecione a tabela `Z_GRUPOUSUARIOS`
2. Adicione as colunas: `NOME`, `EMAIL`
3. Em WHERE, adicione: `Z_GRUPOUSUARIOS.NOME LIKE '%Silva%'`
4. Em ORDER BY, adicione: `NOME ASC`
5. Clique em **"Gerar SQL"**

**SQL Gerado:**
```sql
SELECT Z_GRUPOUSUARIOS.NOME, Z_GRUPOUSUARIOS.EMAIL
FROM Z_GRUPOUSUARIOS
WHERE Z_GRUPOUSUARIOS.NOME LIKE '%Silva%'
ORDER BY NOME ASC;
```

### Exemplo 2: Consulta com INNER JOIN

**Objetivo:** Listar processos ativos com o nome do usuário responsável

**Passos:**
1. Selecione `PR_PROCESSOS` e adicione: `NUMERO`, `STATUS`
2. Selecione `Z_GRUPOUSUARIOS` e adicione: `NOME`
3. Adicione um JOIN:
   - Tipo: INNER
   - Tabela: Z_GRUPOUSUARIOS
   - Esquerda: PR_PROCESSOS.USUARIO
   - Direita: Z_GRUPOUSUARIOS.HANDLE
4. Em WHERE: `PR_PROCESSOS.STATUS = 'ATIVO'`
5. Gere o SQL

**SQL Gerado:**
```sql
SELECT PR_PROCESSOS.NUMERO, PR_PROCESSOS.STATUS, Z_GRUPOUSUARIOS.NOME
FROM PR_PROCESSOS
INNER JOIN Z_GRUPOUSUARIOS ON PR_PROCESSOS.USUARIO = Z_GRUPOUSUARIOS.HANDLE
WHERE PR_PROCESSOS.STATUS = 'ATIVO'
ORDER BY PR_PROCESSOS.NUMERO ASC;
```

### Exemplo 3: Consulta com LEFT JOIN

**Objetivo:** Listar todos os departamentos e seus processos (incluindo departamentos sem processos)

**Passos:**
1. Selecione `PR_DEPARTAMENTOS` e adicione: `NOME`
2. Selecione `PR_PROCESSOS` e adicione: `NUMERO`
3. Adicione um JOIN:
   - Tipo: LEFT
   - Tabela: PR_PROCESSOS
   - Esquerda: PR_DEPARTAMENTOS.HANDLE
   - Direita: PR_PROCESSOS.DEPARTAMENTO
4. Gere o SQL

**SQL Gerado:**
```sql
SELECT PR_DEPARTAMENTOS.NOME, PR_PROCESSOS.NUMERO
FROM PR_DEPARTAMENTOS
LEFT JOIN PR_PROCESSOS ON PR_DEPARTAMENTOS.HANDLE = PR_PROCESSOS.DEPARTAMENTO;
```

### Exemplo 4: Consulta com Agregação

**Objetivo:** Contar processos por departamento

**Passos:**
1. Selecione `PR_DEPARTAMENTOS` e adicione: `NOME`
2. Configure JOIN com `PR_PROCESSOS` (LEFT JOIN)
3. Em GROUP BY: `PR_DEPARTAMENTOS.NOME`
4. Em LIMIT: `10`
5. Gere o SQL

**Nota:** Para adicionar funções de agregação como COUNT, você pode editar o SQL gerado ou usar a seleção de colunas com nomes customizados.

## Uso Programático (API)

### Listando Tabelas

```bash
curl http://localhost:5000/api/tables
```

**Resposta:**
```json
{
  "success": true,
  "tables": ["TABLE1", "TABLE2", ...]
}
```

### Consultando Colunas

```bash
curl http://localhost:5000/api/tables/Z_GRUPOUSUARIOS/columns
```

**Resposta:**
```json
{
  "success": true,
  "table": "Z_GRUPOUSUARIOS",
  "columns": [
    {
      "name": "HANDLE",
      "type": "Integer",
      "nullable": "No",
      "description": "User ID"
    },
    ...
  ]
}
```

### Gerando SQL

```bash
curl -X POST http://localhost:5000/api/build-query \
  -H "Content-Type: application/json" \
  -d '{
    "columns": [
      {"table": "Z_GRUPOUSUARIOS", "column": "NOME"}
    ],
    "joins": [],
    "where": [],
    "orderBy": [],
    "groupBy": [],
    "limit": null,
    "autoInferJoins": false
  }'
```

## Dicas e Truques

### 1. Tipos de JOIN

- **INNER JOIN:** Retorna apenas registros com correspondência em ambas as tabelas
- **LEFT JOIN:** Retorna todos os registros da tabela esquerda, com ou sem correspondência
- **RIGHT JOIN:** Retorna todos os registros da tabela direita, com ou sem correspondência
- **FULL OUTER JOIN:** Retorna todos os registros quando há correspondência em qualquer tabela

### 2. Otimização de Consultas

- Use **INNER JOIN** quando precisar apenas de dados relacionados
- Use **LEFT JOIN** quando quiser manter todos os registros da tabela principal
- Adicione **LIMIT** para testar consultas antes de executar em grandes volumes
- Use índices nas colunas usadas em JOINs e WHERE para melhor performance

### 3. Condições WHERE Complexas

Você pode usar operadores SQL padrão:
- `=`, `!=`, `<`, `>`, `<=`, `>=`
- `LIKE` para padrões de texto
- `IN` para listas de valores
- `BETWEEN` para intervalos
- `IS NULL`, `IS NOT NULL`

**Exemplos:**
```sql
VALOR BETWEEN 1000 AND 5000
STATUS IN ('ATIVO', 'PENDENTE', 'APROVADO')
DATA >= '2024-01-01'
NOME IS NOT NULL
```

### 4. Atalhos de Teclado (Planejado)

- `Ctrl + Enter`: Gerar SQL
- `Ctrl + C`: Copiar SQL
- `Ctrl + R`: Resetar tudo

## Solução de Problemas

### Problema: Nenhuma tabela aparece no dropdown

**Solução:**
1. Verifique se o arquivo `Dicionario de Dados.txt` está no diretório raiz
2. Reinicie o servidor Flask
3. Verifique o console para mensagens de erro

### Problema: SQL gerado está incorreto

**Solução:**
1. Verifique se todas as configurações de JOIN estão corretas
2. Certifique-se de que as colunas especificadas existem nas tabelas
3. Verifique a sintaxe das condições WHERE

### Problema: Erro ao gerar SQL

**Solução:**
1. Certifique-se de ter selecionado pelo menos uma coluna
2. Verifique se os JOINs estão completos (todas as tabelas e colunas especificadas)
3. Revise as condições WHERE para erros de sintaxe

## Suporte e Contribuições

Para reportar bugs ou sugerir melhorias:
- Abra uma issue no GitHub
- Envie um pull request com suas alterações
- Entre em contato com o time de desenvolvimento

## Licença

Este projeto está sob a licença MIT. Consulte o arquivo LICENSE para mais detalhes.

---

**Versão:** 1.0.0  
**Última Atualização:** 2024-12-02
