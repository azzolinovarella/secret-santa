# Secret Santa 🎅
Um aplicativo web para realizar sorteios de Amigo Secreto de forma segura e automatizada, com suporte a envio de mensagens via WhatsApp.

## 📋 Propósito
Este projeto facilita a organização de eventos de _Secret Santa_ (Amigo Secreto) permitindo:
- **Sorteio justo**: Múltiplos algoritmos de sorteio (DFS, Las Vegas);
- **Restrições customizáveis**: Define quem não pode tirar quem;
- **Integração WhatsApp**: Envia resultados automaticamente via WAHA (WhatsApp HTTP API);
- **Segurança**: Criptografia de resultados com chaves personalizadas;
- **Interface amigável**: Aplicação web desenvolvida com Streamlit.

## 🏗️ Estrutura do Projeto
```
secret-santa/
├── src/                        # Código fonte principal
│   ├── app/                    # Camada de aplicação (UI)
│   │   ├── flow.py             # Fluxo principal da aplicação
│   │   ├── handlers.py         # Manipuladores de eventos do formulário
│   │   ├── renderers.py        # Componentes visuais do Streamlit
│   │   └── utils.py            # Utilitários da aplicação
│   ├── domain/                 # Lógica de negócio
│   │   └── secret_santa.py     # Classe principal do sorteio
│   ├── drawers/                # Algoritmos de sorteio
│   │   ├── base.py             # Interface base
│   │   ├── dfs.py              # Algoritmo DFS
│   │   └── las_vegas.py        # Algoritmo Las Vegas
│   ├── integration/            # Integrações externas
│   │   └── waha.py             # Integração com WhatsApp
│   ├── exceptions/             # Exceções customizadas
│   │   └── draw_exceptions.py  # Exceções customizadas de sorteio
│   └── logger/                 # Configuração de logs
│       └── setup_logging.py    # Definição do logger e configuração
├── main.py                     # Ponto de entrada da aplicação
├── Dockerfile                  # Containerização
├── docker-compose.yml          # Orquestração de containers
├── Makefile                    # Automatização de tarefas
├── pyproject.toml              # Configuração e dependências do projeto
└── README.md                   # Este arquivo
```

## 🚀 Como Executar
### Pré-requisitos
- Docker e Docker Compose instalados

### Fluxo de Execução
```bash
# 1. Compilar e iniciar
make up

# 2. Acessar a aplicação em http://localhost:8501

# 3. Parar a aplicação
make down
```

### Comandos Adicionais
Para maior flexibilidade, você pode usar outros comandos do Make:

```bash
# Compilar a imagem (primeira vez)
make build

# Iniciar containers já criados (após first build)
make start

# Parar containers sem removê-los (preserva configuração)
make stop

# Remover containers e volumes (limpeza completa)
make down
```

> **Nota**: É necessário configurar um arquivo `.env` na raiz do projeto com as variáveis necessárias para a integração com WAHA conforme seu ambiente (vide exemplo `.env.example`).
