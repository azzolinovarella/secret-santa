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
- ou Python 3.13+ e pip/uv configurados

### Variáveis de Ambiente
Configure um arquivo `.env` na raiz do projeto com as variáveis necessárias para a integração com WAHA e outras configurações específicas do seu ambiente.

### Execução via Make
```bash
# Compilar a imagem Docker
make build

# Iniciar a aplicação
make up

# Visualizar logs
make logs

# Parar a aplicação
make stop

# Remover containers e volumes
make down
```
