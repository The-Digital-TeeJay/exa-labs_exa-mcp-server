# Exa MCP Server - FastMCP Implementation

Um servidor MCP (Model Context Protocol) para pesquisa web usando a API Exa AI, implementado com [FastMCP](https://github.com/jlowin/fastmcp).

## 🚀 Características

- **Pesquisa Web Inteligente**: Use a API Exa AI para pesquisas semânticas avançadas
- **Múltiplos Transportes**: Suporte para STDIO, HTTP e SSE
- **Cache de Buscas**: Armazena resultados recentes para acesso rápido
- **Pronto para Deploy**: Dockerfile e docker-compose incluídos
- **Type-Safe**: Validação com Pydantic

## 📦 Instalação

### Usando pip

```bash
cd fastmcp_server
pip install -r requirements.txt
```

### Usando uv (recomendado)

```bash
cd fastmcp_server
uv pip install -r requirements.txt
```

## ⚙️ Configuração

1. Copie o arquivo de exemplo de ambiente:

```bash
cp .env.example .env
```

2. Configure sua chave da API Exa:

```env
EXA_API_KEY=sua_chave_api_aqui
```

Obtenha sua chave em: https://exa.ai

## 🔧 Uso

### Modo STDIO (para clientes MCP locais como Claude Desktop)

```bash
python server.py
```

### Modo HTTP (para deploy web)

```bash
python server.py --http
```

O servidor estará disponível em: `http://localhost:8000/mcp`

### Modo SSE (Server-Sent Events)

```bash
python server.py --sse
```

### Usando FastMCP CLI

```bash
# Executar servidor
fastmcp run server.py

# Inspecionar servidor
fastmcp inspect server.py
```

## 🐳 Deploy com Docker

### Build e Run

```bash
docker build -t exa-mcp-server .
docker run -p 8000:8000 -e EXA_API_KEY=sua_chave exa-mcp-server
```

### Usando Docker Compose

```bash
# Configure EXA_API_KEY no .env
docker-compose up -d
```

## 🛠️ Ferramentas Disponíveis

### `search`
Pesquisa na web usando Exa AI.

**Parâmetros:**
- `query` (string, obrigatório): A consulta de pesquisa
- `num_results` (int, opcional): Número de resultados (1-50, padrão: 10)

### `find_similar`
Encontra conteúdo similar a uma URL específica.

**Parâmetros:**
- `url` (string, obrigatório): URL para encontrar conteúdo similar
- `num_results` (int, opcional): Número de resultados (1-50, padrão: 10)

### `get_contents`
Obtém o conteúdo de documentos específicos pelos IDs do Exa.

**Parâmetros:**
- `ids` (list[string], obrigatório): Lista de IDs de documentos Exa

## 📚 Recursos Disponíveis

### `exa://searches`
Lista todas as pesquisas recentes em cache.

### `exa://searches/{index}`
Obtém um resultado de pesquisa específico pelo índice.

## 🔌 Configuração no Claude Desktop

Adicione ao seu `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "exa-search": {
      "command": "python",
      "args": ["/caminho/para/fastmcp_server/server.py"],
      "env": {
        "EXA_API_KEY": "sua_chave_api"
      }
    }
  }
}
```

### Para servidor HTTP remoto:

```json
{
  "mcpServers": {
    "exa-search": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

## 🌐 Deploy em Produção

### FastMCP Cloud

O FastMCP suporta deploy direto para FastMCP Cloud:

```bash
fastmcp deploy server.py
```

### Outras Plataformas

O servidor pode ser deployado em qualquer plataforma que suporte Python:

- **Railway**: Deploy direto do repositório
- **Render**: Configure como Web Service
- **Fly.io**: Use o Dockerfile incluído
- **AWS/GCP/Azure**: Deploy como container

## 📝 Estrutura do Projeto

```
fastmcp_server/
├── server.py           # Servidor MCP principal
├── requirements.txt    # Dependências Python
├── pyproject.toml      # Configuração do projeto
├── Dockerfile          # Imagem Docker
├── docker-compose.yml  # Compose para deploy
└── README.md           # Esta documentação
```

## 🧪 Testando

```bash
# Instalar dependências de dev
pip install -e ".[dev]"

# Rodar testes
pytest
```

## 📄 Licença

MIT License - veja o arquivo LICENSE para detalhes.

## 🔗 Links

- [FastMCP Documentation](https://gofastmcp.com)
- [Exa AI](https://exa.ai)
- [Model Context Protocol](https://modelcontextprotocol.io)

