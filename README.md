# SQL Builder Agent - BENNER

Um agente inteligente para construir consultas SQL com seletor de tabelas e colunas, incluindo suporte para JOINs (LEFT e INNER).

## 🚀 Características

- ✅ Interface web moderna e intuitiva
- ✅ Seleção de múltiplas tabelas e colunas
- ✅ Configuração de JOINs (INNER, LEFT, RIGHT, FULL OUTER)
- ✅ Suporte para cláusulas WHERE, ORDER BY, GROUP BY e LIMIT
- ✅ Inferência automática de JOINs baseada no schema
- ✅ Carregamento automático do esquema do banco de dados
- ✅ Exportação de SQL gerado
- ✅ Interface em Português (Brasil)

## 📋 Pré-requisitos

- Python 3.7 ou superior
- pip (gerenciador de pacotes Python)

## 🔧 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/samuelbahia/BENNER.git
cd BENNER
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

## 🎯 Como Usar

### Iniciando o Servidor

```bash
python app.py
```

O servidor irá iniciar em `http://localhost:5000`

### Usando a Interface Web

1. **Abra seu navegador** e acesse `http://localhost:5000`

2. **Selecione uma Tabela**: Escolha uma tabela do menu dropdown

3. **Adicione Colunas**: Clique no botão "Adicionar" ao lado das colunas desejadas

4. **Configure JOINs**: 
   - Clique em "+ Adicionar Join"
   - Selecione o tipo de JOIN (INNER, LEFT, RIGHT, FULL OUTER)
   - Configure as tabelas e colunas para o JOIN

5. **Adicione Condições** (opcional):
   - WHERE: Adicione condições de filtro
   - ORDER BY: Defina ordenação
   - GROUP BY: Configure agrupamento
   - LIMIT: Limite o número de resultados

6. **Gere o SQL**: Clique no botão "🚀 Gerar SQL"

7. **Copie o SQL**: Use o botão "📋 Copiar SQL" para copiar a consulta

### Usando Programaticamente

```python
from sql_builder_agent import SQLBuilderAgent, JoinType, Table, Column

# Criar uma instância do agente
agent = SQLBuilderAgent()

# Criar tabelas
users_table = Table(name="USERS")
users_table.columns = [
    Column(name="HANDLE", table="USERS", data_type="Integer", nullable=False),
    Column(name="NAME", table="USERS", data_type="Varchar(80)", nullable=False),
]

orders_table = Table(name="ORDERS")
orders_table.columns = [
    Column(name="HANDLE", table="ORDERS", data_type="Integer", nullable=False),
    Column(name="USER_ID", table="ORDERS", data_type="Integer", nullable=False),
    Column(name="TOTAL", table="ORDERS", data_type="Number", nullable=False),
]

# Adicionar tabelas ao agente
agent.add_table(users_table)
agent.add_table(orders_table)

# Selecionar colunas
agent.select_column("USERS", "NAME")
agent.select_column("ORDERS", "TOTAL")

# Adicionar JOIN
agent.add_join(
    JoinType.INNER,
    "ORDERS",
    "USERS", "HANDLE",
    "ORDERS", "USER_ID"
)

# Adicionar condições
agent.add_where("ORDERS.TOTAL > 100")
agent.add_order_by("USERS.NAME", ascending=True)

# Gerar SQL
sql = agent.build_query()
print(sql)
```

## 📊 Estrutura do Projeto

```
BENNER/
├── app.py                      # Aplicação Flask
├── sql_builder_agent.py        # Lógica do agente SQL
├── templates/
│   └── index.html             # Interface web
├── requirements.txt           # Dependências Python
├── README.md                  # Esta documentação
└── Dicionario de Dados.txt   # Schema do banco de dados
```

## 🔍 API REST

### GET /api/tables
Retorna a lista de todas as tabelas disponíveis.

**Resposta:**
```json
{
  "success": true,
  "tables": ["TABLE1", "TABLE2", ...]
}
```

### GET /api/tables/{table_name}/columns
Retorna as colunas de uma tabela específica.

**Resposta:**
```json
{
  "success": true,
  "table": "TABLE_NAME",
  "columns": [
    {
      "name": "COLUMN1",
      "type": "Integer",
      "nullable": "No",
      "description": "Column description"
    }
  ]
}
```

### POST /api/build-query
Gera uma consulta SQL baseada nas seleções.

**Request Body:**
```json
{
  "columns": [
    {"table": "TABLE1", "column": "COL1"},
    {"table": "TABLE2", "column": "COL2"}
  ],
  "joins": [
    {
      "type": "INNER",
      "table": "TABLE2",
      "leftTable": "TABLE1",
      "leftColumn": "ID",
      "rightTable": "TABLE2",
      "rightColumn": "TABLE1_ID"
    }
  ],
  "where": ["TABLE1.STATUS = 'ACTIVE'"],
  "orderBy": [{"column": "TABLE1.NAME", "ascending": true}],
  "groupBy": ["TABLE1.CATEGORY"],
  "limit": 100,
  "autoInferJoins": false
}
```

**Resposta:**
```json
{
  "success": true,
  "query": "SELECT TABLE1.COL1, TABLE2.COL2\nFROM TABLE1\nINNER JOIN TABLE2 ON TABLE1.ID = TABLE2.TABLE1_ID\nWHERE TABLE1.STATUS = 'ACTIVE'\nGROUP BY TABLE1.CATEGORY\nORDER BY TABLE1.NAME ASC\nLIMIT 100;"
}
```

## 🎨 Capturas de Tela

A interface possui:
- Design moderno com gradientes
- Seleção fácil de tabelas e colunas
- Configuração visual de JOINs
- Visualização do SQL gerado com syntax highlighting
- Feedback visual para todas as ações

## 🛠️ Desenvolvimento

### Executar em Modo Debug

```bash
python app.py
```

### Executar Testes

```bash
python sql_builder_agent.py
```

## 📝 Exemplos de SQL Gerado

### Exemplo 1: Consulta Simples
```sql
SELECT Z_GRUPOUSUARIOS.NOME, Z_GRUPOUSUARIOS.EMAIL
FROM Z_GRUPOUSUARIOS
WHERE Z_GRUPOUSUARIOS.NOME LIKE '%Silva%'
ORDER BY Z_GRUPOUSUARIOS.NOME ASC;
```

### Exemplo 2: Com INNER JOIN
```sql
SELECT PR_PROCESSOS.NUMERO, Z_GRUPOUSUARIOS.NOME
FROM PR_PROCESSOS
INNER JOIN Z_GRUPOUSUARIOS ON PR_PROCESSOS.USUARIO = Z_GRUPOUSUARIOS.HANDLE
WHERE PR_PROCESSOS.STATUS = 'ATIVO'
ORDER BY PR_PROCESSOS.NUMERO ASC;
```

### Exemplo 3: Com LEFT JOIN e Agrupamento
```sql
SELECT PR_DEPARTAMENTOS.NOME, COUNT(PR_PROCESSOS.HANDLE) as TOTAL
FROM PR_DEPARTAMENTOS
LEFT JOIN PR_PROCESSOS ON PR_DEPARTAMENTOS.HANDLE = PR_PROCESSOS.DEPARTAMENTO
GROUP BY PR_DEPARTAMENTOS.NOME
ORDER BY TOTAL DESC
LIMIT 10;
```

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor, sinta-se à vontade para enviar pull requests.

## 📄 Licença

Este projeto está sob a licença MIT.

## 👥 Autor

Samuel Bahia

## 📞 Suporte

Para questões ou suporte, por favor abra uma issue no GitHub.

---

**Nota**: Esta ferramenta é projetada para auxiliar na construção de consultas SQL. Sempre revise o SQL gerado antes de executá-lo em um ambiente de produção.
