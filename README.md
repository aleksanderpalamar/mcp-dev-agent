# MCP Development Agent

Um agente de desenvolvimento baseado no protocolo Model Context Protocol (MCP) que oferece funcionalidades de memória, documentação e integração com Git/GitHub, disponível tanto em modo CLI quanto como servidor SSE.

## Funcionalidades

- 🧠 **Sistema de Memória**: Armazena e recupera informações usando embeddings via ChromaDB
- 📚 **Busca em Documentação**: Pesquisa em arquivos de documentação
- 🔄 **Integração Git**: Consulta histórico de commits e issues
- 🔍 **Análise de Código**: Análise estática de código usando tree-sitter
- 🌐 **Integração GitHub**: Busca repositórios, issues e código no GitHub
- 💻 **Interface CLI**: Interface de linha de comando interativa
- 🌐 **Modo Servidor**: Suporte a Server-Sent Events (SSE)

## Requisitos

- Python 3.x
- ChromaDB
- GitPython
- FastMCP
- PyGithub
- tree-sitter

## Instalação

1. Clone o repositório:

```bash
git clone [url-do-repositorio]
cd mcp-dev-agent
```

2. Instale as dependências:

```bash
pip install -r requirements.txt
```

3. Configure as variáveis de ambiente (copie .env.example para .env):

```bash
cp .env.example .env
# Edite .env com suas chaves de API
```

4. Configure os parsers de código:

```bash
python setup_parsers.py
```

## Uso

O agente pode ser executado em dois modos:

### Modo CLI

```bash
python main.py --mode cli
```

Comandos disponíveis:

#### Memória

- `/memory add <conteúdo>` - Adiciona uma nova memória geral
- `/memory get <consulta>` - Busca memórias existentes
- `/memory repo add <conteúdo>` - Adiciona uma memória específica do repositório
- `/memory repo get <consulta>` - Busca memórias específicas do repositório

#### Git e GitHub

- `/git commits [número]` - Mostra histórico de commits (padrão: 5 últimos)
- `/git issues` - Lista issues do repositório local
- `/git info` - Mostra informações detalhadas do repositório
- `/git diff` - Mostra alterações pendentes (staged e unstaged)
- `/github repo <owner/repo>` - Mostra detalhes de um repositório no GitHub
- `/github issues <owner/repo> [state]` - Lista issues do GitHub (state: open/closed)
- `/github search <query> [language]` - Busca código no GitHub

#### Análise de Código

- `/code analyze <arquivo> [language]` - Analisa estrutura do código (funções, classes, imports)

#### Documentação

- `/docs <consulta>` - Pesquisa na documentação
- `exit` - Sai do modo CLI

### Recursos Avançados

#### Análise de Código

O sistema utiliza tree-sitter para analisar código em:

- Python
- JavaScript
- TypeScript

A análise inclui:

- Extração de funções e métodos
- Identificação de classes
- Mapeamento de imports
- Integração com memória para contexto

#### Integração GitHub

- Informações detalhadas de repositórios
- Busca e listagem de issues
- Busca de código com filtro por linguagem
- Metadados enriquecidos

#### Sistema de Memória Aprimorado

- Suporte a diferentes tipos de contexto
- Metadados enriquecidos
- Busca contextual
- Histórico temporal
- Integração com análise de código

### Modo Servidor (SSE)

```bash
python main.py
# ou
python main.py --mode server
```

O servidor SSE permite integração com outras aplicações através do protocolo MCP.

## Estrutura do Projeto

```
.
├── main.py              # Ponto de entrada da aplicação
├── setup_parsers.py     # Configuração dos parsers de código
├── tools/
│   ├── memory_tool.py   # Gerenciamento de memória via ChromaDB
│   ├── doc_tool.py      # Busca em documentação
│   ├── git_tool.py      # Integração com Git
│   └── github_tool.py   # Integração com GitHub e análise de código
└── docs/
    └── api_reference.md # Documentação de referência da API
```

## Configuração dos Modelos de IA

O agente suporta integração com modelos de IA da Anthropic (Claude) e OpenAI (GPT-4 e GPT-3.5). Para usar esses modelos, você precisa:

1. Configurar as variáveis de ambiente:

```bash
export ANTHROPIC_API_KEY="sua_chave_api_anthropic"
export OPENAI_API_KEY="sua_chave_api_openai"
```

2. O arquivo `.agent.json` já está configurado com:

- Claude-3 Opus como modelo padrão
- Suporte a GPT-4 Turbo e GPT-3.5 Turbo
- Cache de respostas (24 horas)
- Logging de interações

### Parâmetros dos Modelos

Você pode ajustar os parâmetros dos modelos editando o arquivo `.agent.json`:

- `temperature`: Controla a criatividade das respostas (0.0 a 1.0)
- `max_tokens`: Limite máximo de tokens por resposta
- `top_p`: Controla a diversidade das respostas
