# 💡 Exemplos de Uso

## Cenários Comuns

### 1. Encontrar uma Tabela Específica

**Objetivo**: Localizar a tabela `GN_PESSOAS`

**Passos**:
1. Digite "PESSOAS" na caixa de busca
2. A lista filtrará automaticamente
3. Clique em `GN_PESSOAS` para ver detalhes

**Resultado**: Você verá todos os campos da tabela de pessoas, incluindo HANDLE, NOME, CPF, etc.

---

### 2. Explorar um Módulo Completo

**Objetivo**: Ver todas as tabelas do módulo de Processos (PR)

**Passos**:
1. Na seção "Módulos", clique em "PR - Processos"
2. A lista mostrará apenas tabelas PR_*
3. Navegue pelas 247 tabelas do módulo

**Dica**: O número ao lado do módulo indica a quantidade de tabelas.

---

### 3. Entender Relacionamentos

**Objetivo**: Ver como `PR_PROCESSOS` se relaciona com outras tabelas

**Passos**:
1. Busque e selecione `PR_PROCESSOS`
2. Clique na aba "Relacionamentos"
3. Veja os cards de relacionamento
4. Clique em qualquer card para navegar à tabela relacionada

**Exemplo**: Se `PR_PROCESSOS` tem FK para `GN_PESSOAS`, você verá um card indicando essa relação.

---

### 4. Verificar Campos Obrigatórios

**Objetivo**: Saber quais campos são NOT NULL em `EJ_CONTRATOS`

**Passos**:
1. Selecione `EJ_CONTRATOS`
2. Na aba "Campos", veja a coluna "Obrigatório"
3. Campos com badge vermelho "Obrigatório" são NOT NULL
4. Campos com badge verde "Opcional" podem ser NULL

---

### 5. Analisar Tipos de Dados

**Objetivo**: Ver a distribuição de tipos em uma tabela

**Passos**:
1. Selecione qualquer tabela
2. Clique na aba "Estatísticas"
3. Veja o gráfico de distribuição de tipos
4. Os cards mostram totais de campos obrigatórios/opcionais

---

### 6. Busca por Campo

**Objetivo**: Encontrar todas as tabelas que têm um campo "HANDLE"

**Passos**:
1. Digite "HANDLE" na busca
2. A busca encontrará tabelas onde:
   - O nome contém "HANDLE"
   - Algum campo se chama "HANDLE"
   - A descrição menciona "HANDLE"

**Resultado**: Praticamente todas as tabelas aparecerão, pois HANDLE é a PK padrão.

---

### 7. Seguir Chave Estrangeira

**Objetivo**: Navegar de `PR_PROCESSOS.EMPRESA` para `EMPRESAS`

**Passos**:
1. Selecione `PR_PROCESSOS`
2. Na aba "Campos", localize o campo `EMPRESA`
3. Se houver FK, aparecerá um link na coluna "FK"
4. Clique no link para ir à tabela referenciada

---

### 8. Comparar Módulos

**Objetivo**: Entender a estrutura dos módulos GN (Geral) e PR (Processos)

**Passos**:
1. Selecione módulo "GN - Geral"
2. Note o padrão: cadastros básicos (pessoas, empresas, bancos)
3. Selecione módulo "PR - Processos"
4. Note o padrão: tabelas transacionais (processos, pedidos, eventos)

---

## Casos de Uso Práticos

### Para Desenvolvedores

```
Cenário: Criar nova funcionalidade que envolve processos
1. Explorar módulo PR (Processos)
2. Identificar tabelas principais (PR_PROCESSOS)
3. Ver campos disponíveis
4. Verificar FKs para outras tabelas
5. Entender relacionamentos
```

### Para Analistas

```
Cenário: Documentar modelo de dados
1. Navegar por todos os módulos
2. Exportar estatísticas (copiar do JSON)
3. Identificar tabelas-chave por módulo
4. Mapear relacionamentos importantes
```

### Para DBAs

```
Cenário: Otimizar banco de dados
1. Identificar tabelas com muitos campos (via contador)
2. Analisar distribuição de tipos
3. Verificar campos nullable
4. Identificar tabelas muito relacionadas
```

### Para Novos Membros

```
Cenário: Onboarding - entender o sistema
1. Começar pelo módulo GN (cadastros gerais)
2. Explorar GN_PESSOAS, GN_EMPRESAS
3. Seguir para módulos específicos
4. Usar busca para encontrar entidades de interesse
```

---

## Dicas Avançadas

### Atalhos de Busca

| Busca | Resultado |
|-------|-----------|
| `PR_` | Todas as tabelas de Processos |
| `INTEGER` | Campos do tipo Integer (indiretamente) |
| `HANDLE` | Praticamente todas as tabelas (PK padrão) |
| `NOME` | Tabelas com campo NOME |
| `EMPRESA` | Tabelas relacionadas a empresas |

### Padrões do Sistema

- **HANDLE**: Chave primária
- **Z_GRUPO**: Grupo/segurança
- **INCLUIDOEM/INCLUIDOPOR**: Auditoria de criação
- **ALTERADOEM/ALTERADOPOR**: Auditoria de alteração

### Prefixos Comuns

| Prefixo | Significado |
|---------|-------------|
| GN_ | Geral (cadastros base) |
| PR_ | Processos |
| EJ_ | Extrajudicial |
| FI_ | Financeiro |
| CA_ | Cálculos |
| ES_ | eSocial |
| PI_ | Propriedade Intelectual |
| WF_ | Workflow |
