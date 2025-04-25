# MCP Development Agent

Um agente de desenvolvimento baseado no protocolo Model Context Protocol (MCP) que oferece funcionalidades de memória, documentação e integração com Git, disponível tanto em modo CLI quanto como servidor SSE.

## Funcionalidades

- 🧠 **Sistema de Memória**: Armazena e recupera informações usando embeddings via ChromaDB
- 📚 **Busca em Documentação**: Pesquisa em arquivos de documentação
- 🔄 **Integração Git**: Consulta histórico de commits e issues
- 💻 **Interface CLI**: Interface de linha de comando interativa
- 🌐 **Modo Servidor**: Suporte a Server-Sent Events (SSE)

## Requisitos

- Python 3.x
- ChromaDB
- GitPython
- FastMCP

## Instalação

1. Clone o repositório:

```bash
git clone [url-do-repositorio]
cd mcp-dev-agent
```

2. Instale as dependências:

```bash
pip install chromadb GitPython fastmcp
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

#### Git

- `/git commits [número]` - Mostra histórico de commits (padrão: 5 últimos)
- `/git issues` - Lista issues do repositório
- `/git info` - Mostra informações detalhadas do repositório
- `/git diff` - Mostra alterações pendentes (staged e unstaged)

#### Documentação

- `/docs <consulta>` - Pesquisa na documentação
- `exit` - Sai do modo CLI

### Recursos Avançados

#### Memória do Repositório

O sistema mantém um histórico contextualizado das mudanças no repositório, incluindo:

- Estado atual do branch
- Commits recentes
- Alterações pendentes
- Metadados do contexto

#### Integração Git

- Informações detalhadas do repositório (branch, remotes, status)
- Visualização de diffs com contexto
- Monitoramento automático de mudanças
- Armazenamento inteligente do contexto

#### Sistema de Memória Aprimorado

- Suporte a diferentes tipos de contexto
- Metadados enriquecidos
- Busca contextual
- Histórico temporal

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
├── tools/
│   ├── memory_tool.py   # Gerenciamento de memória via ChromaDB
│   ├── doc_tool.py      # Busca em documentação
│   └── git_tool.py      # Integração com Git
└── docs/
    └── api_reference.md # Documentação de referência da API
```

## Ferramentas

### Memory Tool

Utiliza ChromaDB para armazenar e recuperar informações com suporte a embeddings, permitindo buscas semânticas eficientes.

### Doc Tool

Permite buscar informações em arquivos de documentação, facilitando o acesso rápido a referências e guias.

### Git Tool

Oferece integração com Git para consulta de histórico de commits e issues (requer configuração adicional para GitHub/GitLab API).

## Contribuindo

1. Fork o projeto
2. Crie sua feature branch (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Crie um Pull Request

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.

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
