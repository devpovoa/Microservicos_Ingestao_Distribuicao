# Microserviços de Ingestão e Distribuição de Dados

## Visão Geral

Este projeto é composto por **dois microserviços independentes** que se comunicam de forma assíncrona via **RabbitMQ** e **Celery**, permitindo um fluxo de ingestão, processamento e distribuição de dados de forma desacoplada e escalável.

* **Microserviço 1 - Ingestão (FastAPI + JWT + SQLAlchemy)**
  
  * Monitora uma pasta de arquivos.
  * Lê arquivos `vendas.xlsx` com **Pandas**.
  * Aceita também comunicação externa via `JSON` para ingestão de dados via API.
  * Realiza pré-processamento e persiste os dados em tabelas temporárias (`ClienteTemp`, `CompraTemp`, `ProdutoTemp`) usando **SQLAlchemy**.
  * Valida os dados e envia mensagens JSON para uma fila RabbitMQ (`processed_data`).
  * Possui autenticação JWT para controle de acesso.

* **Microserviço 2 - Distribuição (Django) - Em Construção**
  
  * Consome as mensagens da fila RabbitMQ.
  * Persiste os dados de forma definitiva no banco de dados normalizado.
  * Apresenta dashboards e relatórios por meio de templates HTML.
  * Não expõe uma API pública, apenas interfaces web administrativas e de visualização.

O projeto é **containerizado com Docker** para garantir portabilidade e fácil deploy.

---

## Tecnologias Utilizadas

* **Linguagem e Frameworks**
  
  * [Python 3.11+](https://www.python.org/)
  * [FastAPI](https://fastapi.tiangolo.com/) para o microserviço de ingestão
  * [Django 5+](https://www.djangoproject.com/) para o microserviço de distribuição
  * [Pandas](https://pandas.pydata.org/) para leitura e pré-processamento de arquivos Excel
  * [SQLAlchemy ORM](https://www.sqlalchemy.org/) para persistência no FastAPI

* **Mensageria e Processamento Assíncrono**
  
  * [RabbitMQ](https://www.rabbitmq.com/) para comunicação assíncrona entre serviços
  * [Celery](https://docs.celeryq.dev/) para orquestração de tarefas assíncronas

* **Banco de Dados**
  
  * [PostgreSQL](https://www.postgresql.org/) para persistência temporária e definitiva

* **Ambiente e Deploy**
  
  * [Docker](https://www.docker.com/) e Docker Compose para orquestração dos serviços

---

## Estrutura do Projeto

```
.
├── docker-compose.yml        # Orquestração dos containers
├── .env                      # Variáveis de ambiente
├── micro_ingest/             # Microserviço 1 (FastAPI)
│   ├── app/
│   │   ├── api/              # Endpoints REST para validação/testes
│   │   ├── core/             # Configurações e inicialização do app
│   │   ├── models/           # Tabelas temporárias (SQLAlchemy)
│   │   ├── workers/          # File watcher e integração RabbitMQ
│   │   └── main.py           # Entry point do serviço
│   └── requirements.txt
│
├── micro_distrib/            # Microserviço 2 (Django)
│   ├── distrib/              # Configurações e apps Django
│   ├── templates/            # Dashboards e relatórios
│   └── requirements.txt
│
└── README.md                 # Este arquivo
```

---

## Fluxo de Funcionamento

1. **Ingestão**
   
   * O `file_watcher` monitora a pasta `/app/data`.
   * Quando novos arquivos `vendas.xlsx` são detectados, são lidos com **Pandas**.
   * Também é possível enviar dados diretamente via requisições JSON autenticadas por JWT.
   * Os dados são persistidos em tabelas temporárias no `postgres_ingest`.
   * Após validação, os dados são enviados em formato JSON para a fila `processed_data` no **RabbitMQ**.

2. **Distribuição**
   
   * O microserviço Django consome as mensagens da fila.
   * Os dados são salvos de forma definitiva no `postgres_distrib`, seguindo o modelo normalizado.
   * Os dados processados são exibidos por meio de **templates HTML** e visualizações administrativas.

---

## Monitoramento e Logs

* Logs do serviço de ingestão:
  
  ```bash
  docker logs -f fastapi_ingest
  ```

* Logs do serviço de distribuição:
  
  ```bash
  docker logs -f django_distrib
  ```

* Verificar se RabbitMQ recebeu mensagens:
  
  * Acesse o painel de administração (`http://localhost:15672/`)
  * Veja a fila `processed_data`

---

## Próximos Passos

* Implementar testes automatizados para os microserviços
* Criar visualizações mais avançadas no Django
* Adicionar autenticação JWT no FastAPI
* Configurar CI/CD para deploy automatizado

---

## Licença & Autoria

📄 Este material é de autoria de **[Thiago Povoa](https://github.com/devpovoa)** e pode ser utilizado livremente para fins de estudo.  
Caso utilize em outro projeto, mantenha a referência ao autor.  
