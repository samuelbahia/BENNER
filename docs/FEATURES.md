# ✨ Funcionalidades do Explorador

## 🎯 Visão Geral

O Explorador de Dicionário de Dados é uma ferramenta web moderna e interativa para consultar a estrutura do banco de dados Benner.

## 📊 Interface Principal

### Header
- **Logo e Título**: Identifica a aplicação
- **Estatísticas em Tempo Real**:
  - Total de Tabelas
  - Total de Campos
  - Total de Relacionamentos
  - Total de Módulos

### Sidebar (Barra Lateral)

#### 🔍 Busca
- **Busca instantânea**: Filtra enquanto você digita
- **Busca multi-campo**: Encontra por nome de tabela, nome de campo ou descrição
- **Performance**: Resposta imediata mesmo com milhares de tabelas

#### 📦 Módulos
- **Lista completa**: Todos os módulos do sistema
- **Contador**: Quantidade de tabelas por módulo
- **Filtro rápido**: Clique para ver apenas tabelas do módulo
- **Opção "Todos"**: Voltar a ver todas as tabelas

#### 📋 Lista de Tabelas
- **Ordenação alfabética**: Fácil localização
- **Contador de campos**: Visualize a complexidade
- **Scroll infinito**: Navegue por todas as tabelas
- **Highlight ativo**: Tabela selecionada em destaque

### Painel Central

#### 📝 Aba de Campos
| Coluna | Descrição |
|--------|-----------|
| **Campo** | Nome do campo (MAIÚSCULAS) |
| **Tipo** | Tipo de dado (Integer, Varchar, etc) |
| **Tamanho** | Tamanho máximo para strings |
| **Obrigatório** | Se o campo é NOT NULL |
| **FK** | Referência a outra tabela (clicável) |
| **Descrição** | Explicação do propósito do campo |

**Recursos:**
- Cores por tipo de dado
- Badge visual para obrigatoriedade
- Links para tabelas referenciadas

#### 🔗 Aba de Relacionamentos
- **Cards visuais**: Cada relacionamento em um card
- **Direção**: Setas indicam de/para
- **Navegação**: Clique para ir à tabela relacionada
- **Campo FK**: Mostra qual campo faz a referência

#### 📊 Aba de Estatísticas
**Cards de Resumo:**
- Total de Campos
- Campos Obrigatórios
- Campos Opcionais
- Chaves Estrangeiras

**Gráfico de Tipos:**
- Barras horizontais
- Porcentagem de cada tipo
- Cores distintas por tipo

## 🎨 Design

### Responsividade
- **Desktop**: Layout completo com sidebar fixa
- **Tablet**: Sidebar adaptativa
- **Mobile**: Layout em coluna única

### Temas de Cores
- **Primário**: Azul (#2563eb)
- **Sucesso**: Verde (#10b981)
- **Alerta**: Amarelo (#f59e0b)
- **Erro**: Vermelho (#ef4444)
- **Acento**: Roxo (#8b5cf6)

### Animações
- Transições suaves em hover
- Feedback visual em cliques
- Carregamento sem flicker

## 🔧 Recursos Técnicos

### Performance
- **Zero dependências**: HTML/CSS/JS puros
- **Carregamento rápido**: ~40KB total
- **Busca otimizada**: O(n) com early exit
- **Renderização eficiente**: Virtual DOM pattern

### Compatibilidade
- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

### Acessibilidade
- Navegação por teclado
- Contraste adequado
- Fonte legível
- Labels semânticos

## 📱 Atalhos e Dicas

### Navegação Rápida
1. **Ctrl/Cmd + F**: Foco na busca
2. **Enter**: Seleciona primeiro resultado
3. **Escape**: Limpa busca

### Dicas de Uso
- Use prefixos para busca rápida: `GN_`, `PR_`
- Clique em FKs para navegar entre tabelas
- Use módulos para filtrar por área funcional
- A busca encontra também por descrição de campo

## 📈 Dados Disponíveis

### Estatísticas Gerais
- **1200+** tabelas
- **17000+** campos
- **2400+** relacionamentos
- **50+** módulos

### Tipos de Dados
| Tipo | Descrição | Quantidade |
|------|-----------|------------|
| Integer | Números inteiros | ~9700 |
| Varchar | Texto variável | ~2500 |
| Data | Datas | ~1700 |
| Char | Caractere fixo | ~1500 |
| Number | Decimais | ~1200 |
| Blob | Binário/Texto longo | ~900 |

## 🔄 Atualização de Dados

Para atualizar os dados quando o dicionário mudar:

```bash
# Unix/macOS/Linux
./scripts/generate-datadict.sh

# Windows
scripts\generate-datadict.bat
```

O explorer carregará automaticamente o novo `datadict.json`.
