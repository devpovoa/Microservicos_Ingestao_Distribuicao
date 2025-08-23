# 📊 Microserviços de Ingestão e Distribuição de Dados

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-API-green)
![Django](https://img.shields.io/badge/Django-5.0-green)
![Celery](https://img.shields.io/badge/Celery-Worker-orange)
![RabbitMQ](https://img.shields.io/badge/RabbitMQ-MQ-red)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-DB-blue)
![Docker](https://img.shields.io/badge/Docker-Compose-blue)

---

## 🚀 Sobre o Projeto

Este projeto demonstra a construção de uma **arquitetura moderna baseada em microserviços**, aplicando **boas práticas de desenvolvimento backend**.  
O sistema é dividido em dois serviços independentes e desacoplados:

- **Ingestão (FastAPI + Pandas + SQLAlchemy + JWT)** → processa arquivos e APIs externas, valida dados e envia mensagens para uma fila **RabbitMQ**.  
- **Distribuição (Django + Celery + PostgreSQL)** → consome as mensagens, persiste em um modelo normalizado e exibe os dados em **dashboards e relatórios interativos**.

⚡ O objetivo é mostrar como aplicar **escalabilidade, resiliência e desacoplamento** em um sistema real, combinando **mensageria assíncrona** com **APIs modernas**.

---

## 🏗 Arquitetura

O sistema é composto por **dois microserviços independentes** que se comunicam via **RabbitMQ**.  
Cada serviço tem seu próprio banco de dados PostgreSQL e é orquestrado por **Docker Compose**, garantindo isolamento e reprodutibilidade.

### 🔹 Fluxo Resumido

1. O microserviço **Ingestão (FastAPI)**:
   
   - Monitora uma pasta de arquivos `vendas.xlsx`.
   - Faz pré-processamento com **Pandas**.
   - Persiste dados temporários com **SQLAlchemy**.
   - Publica mensagens JSON na fila `processed_data` (RabbitMQ).
   - Oferece **API REST externa** (endpoints protegidos por **JWT**) que também aceita ingestão de dados em formato JSON.

2. O microserviço **Distribuição (Django + Celery)**:
   
   - Consome a fila `processed_data` de forma assíncrona.
   - Normaliza e persiste dados no banco `postgres_distrib`.
   - Exibe **dashboards e relatórios gerenciais** por meio de templates Django.
   - Fornece interface administrativa via Django Admin.

### 🔹 Visão Geral (Mermaid)

```mermaid
flowchart LR
    A[Excel/JSON via API] --> B(FastAPI Ingestão)
    B -->|Publica JSON| C[(RabbitMQ)]
    C --> D[Celery Worker - Django Distribuição]
    D -->|Normaliza| E[(Postgres Distribuição)]
    E --> F[Dashboard Django]
```

---

## 🛠 Tecnologias Utilizadas

O projeto combina bibliotecas modernas do ecossistema Python para garantir **robustez, segurança e escalabilidade**.  
Abaixo estão as principais dependências de cada microserviço:

### 🔹 Microserviço de Ingestão (FastAPI)

| Tecnologia            | Uso no Projeto                                         |
| --------------------- | ------------------------------------------------------ |
| **FastAPI**           | Framework principal da API de ingestão                 |
| **Uvicorn**           | Servidor ASGI para rodar o FastAPI                     |
| **python-jose**       | Implementação de **JWT** para autenticação             |
| **pydantic-settings** | Gerenciamento de configurações e variáveis de ambiente |
| **SQLAlchemy**        | ORM para persistência temporária                       |
| **psycopg2-binary**   | Driver PostgreSQL                                      |
| **Pandas**            | Leitura e pré-processamento de arquivos Excel          |
| **OpenPyXL**          | Suporte a leitura/escrita de arquivos `.xlsx`          |
| **python-multipart**  | Upload de arquivos                                     |
| **Celery**            | Publicação de mensagens assíncronas para RabbitMQ      |

---

### 🔹 Microserviço de Distribuição (Django)

| Tecnologia                                      | Uso no Projeto                               |
| ----------------------------------------------- | -------------------------------------------- |
| **Django 5.2.5**                                | Framework principal para web/dashboards      |
| **asgiref**                                     | Suporte ao ASGI no Django                    |
| **sqlparse**                                    | Utilitário interno para parsing de SQL       |
| **python-dotenv**                               | Carregamento de variáveis de ambiente        |
| **Celery**                                      | Worker para consumo da fila `processed_data` |
| **psycopg2-binary**                             | Driver PostgreSQL                            |
| **django-crispy-forms** + **crispy-bootstrap5** | Melhorias visuais em formulários Django      |
| **ReportLab**                                   | Geração de relatórios em **PDF**             |

---

## ✅ Funcionalidades Principais

### 🔹 Microserviço de Ingestão (FastAPI)

**Ingestão de dados**

- Monitora a pasta de dados (`/app/data`) e processa arquivos `vendas.xlsx`.
- Aceita **ingestão via API externa** (JSON) para integração com outros sistemas.
- Validação e pré-processamento com **Pandas** (tipos, normalização, limpeza básica).

**Persistência temporária**

- Armazena dados em tabelas temporárias (`ClienteTemp`, `ProdutoTemp`, `CompraTemp`) via **SQLAlchemy**.
- Mantém rastreabilidade de registros processados e pendentes.

**Mensageria**

- Publica eventos em formato **JSON** na fila `processed_data` do **RabbitMQ**.
- Estrutura de mensagem pensada para **idempotência** (campos de referência/identificadores consistentes).

**Segurança**

- **JWT** para proteger endpoints de ingestão externa.
- Configurações via **pydantic-settings** e variáveis de ambiente.

**Operação**

- Documentação interativa via **Swagger** em `/docs` (porta `8001`).
- Logs focados em eventos de ingestão, validação e publicação.

---

### 🔹 Microserviço de Distribuição (Django + Celery)

**Consumo assíncrono**

- **Celery Worker** escuta a fila `processed_data` e processa eventos de forma paralela.
- Estratégia de **upsert**/**normalização** para evitar duplicidades.

**Persistência definitiva**

- Gravação em modelos normalizados no `postgres_distrib` (clientes, produtos, compras, endereços, etc.).
- Integridade relacional garantida (FKs, índices e regras de consistência).

**Visualização e análise**

- **Dashboard gerencial** com KPIs e gráficos.
- Listagens, filtros e **relatórios** (inclui geração de **PDF** com ReportLab).
- Interface **Django Admin** para gestão operacional.

**Operação**

- Aplicação web servindo em `http://localhost:8002`.
- Logs do worker e do web app separados para facilitar troubleshooting.

---

### 🔁 Funcionalidades Transversais

- **Docker Compose** para orquestração dos serviços, bancos e mensageria.
- **Healthchecks** em Postgres e RabbitMQ para garantir ordem de inicialização.
- **Variáveis de ambiente** (`.env`) para credenciais e caminhos (ex.: `HOST_DATA_PATH`).
- **Escalabilidade horizontal** simples (replicar workers Celery para aumentar throughput).

---

## 🚀 Como Rodar

Antes de iniciar, garanta que você tem **Docker** e **Docker Compose** instalados no ambiente.

### 1️⃣ Configurar variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto, no mesmo nível do `docker-compose.yml`:

```env
# RabbitMQ
RABBITMQ_USER=guest
RABBITMQ_PASS=guest
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/

# Caminho absoluto no host para os arquivos de ingestão
HOST_DATA_PATH=/ABSOLUTE/PATH/TO/data

# Fuso horário (opcional)
TZ=America/Sao_Paulo
```

⚠️ **Importante**:

* `HOST_DATA_PATH` deve ser um caminho absoluto válido no seu computador (por exemplo, `/home/thiago/data`).

* Caso contrário, o Docker pode retornar erro:
  
  ```bash
  invalid spec: :/app/data: empty section between colons
  ```
---

### 2️⃣ Subir os serviços

No terminal, execute:

```bash
docker compose up -d --build
```

Isso vai subir todos os containers: RabbitMQ, Postgres (ingest/distrib), FastAPI, Django e Celery Worker.

---

### 3️⃣ Acessos rápidos

* **RabbitMQ Management UI** → [http://localhost:15672](http://localhost:15672)  
  _Usuário/senha definidos no `.env`._

* **FastAPI Ingestão** → [http://localhost:8001](http://localhost:8001)
  
  * Documentação Swagger: [Serviço de Ingestão de Dados - Swagger UI](http://localhost:8001/docs)

* **Django Distribuição** → [http://localhost:8002](http://localhost:8002)
  
  * Admin: [Acessar | Site de administração do Django](http://localhost:8002/admin)

---

### 4️⃣ Configurações iniciais do Django

Após subir os serviços pela primeira vez, rode:

```bash
# Aplicar migrações
docker compose exec django_distrib python manage.py migrate

# Criar superusuário
docker compose exec django_distrib python manage.py createsuperuser

```

Agora você já pode acessar o **Django Admin** e começar a gerenciar os dados processados.

---

### 5️⃣ Logs úteis

Para acompanhar o funcionamento em tempo real:

```bash
# Logs do serviço de ingestão (FastAPI)
docker compose logs -f fastapi_ingest

# Logs do serviço de distribuição (Django)
docker compose logs -f django_distrib

# Logs do worker Celery
docker compose logs -f celery_worker_distrib
```
---

## 🎥 Demonstração (Showcase)

A seguir estão exemplos visuais que mostram o sistema em funcionamento.  
Essas imagens/GIFs dão clareza sobre o fluxo completo: da ingestão de dados até a visualização final no dashboard.

---

### 1️⃣ Ingestão via FastAPI

- **Swagger UI** exibindo endpoints protegidos por JWT.  
  ![swagger](/docs/images/swagger.png)
  ![jwt](/docs/images/jwt.png)
- Exemplo de ingestão de dados via **JSON externo**.  
  ![API Externa](/docs/images/api_dados.png)
  ![Get API](/docs/images/get_api.png)
- Upload de arquivo `vendas.xlsx` sendo processado.
  ![Excel](/docs/images/excell.gif)

---

### 2️⃣ RabbitMQ em ação

- Painel do RabbitMQ exibindo a fila `processed_data`.  
- Demonstração de mensagens entrando na fila após ingestão.  
- Mensagens sendo consumidas pelo worker Celery.

---

### 3️⃣ Dashboard Django

- Tela inicial do **dashboard** com KPIs e gráficos.  
- Exemplo de relatório ou listagem de clientes/compras.  
- Exportação de relatório em **PDF**.

---

### 4️⃣ Django Admin

- Área administrativa para gerenciar clientes, produtos e compras.  
- Exemplo de CRUD básico (inserção, edição ou listagem).  

---

## 🛣 Roadmap

Este projeto está em evolução contínua.  
Abaixo estão os próximos passos planejados, divididos em fases:

### ✅ Fase 1 — Estrutura Base (Concluída)

- [x] Configuração do ambiente com **Docker Compose**
- [x] Microserviço de **Ingestão (FastAPI + Pandas + SQLAlchemy)**
- [x] **API externa (JSON) com JWT** para ingestão (FastAPI)
- [x] Publicação de mensagens em fila **RabbitMQ**
- [x] Microserviço de **Distribuição (Django)**
- [x] Consumo assíncrono com **Celery Worker**
- [x] Persistência em bancos **PostgreSQL** independentes

### ✅ Fase 2 — Funcionalidades Intermediárias (Concluída)

- [x] **Dashboard Django** com KPIs e gráficos (Chart.js / Bootstrap)
- [x] **Relatórios em PDF** com ReportLab
- [x] **Listagens avançadas** com filtros e paginação
- [x] **Exportação de relatórios em Excel/CSV**

### 🚀 Fase 3 — Melhorias Avançadas (Planejado)

- [ ] Testes automatizados com **pytest**
- [ ] **CI/CD com GitHub Actions** (lint, build, testes)
- [ ] Observabilidade: métricas com **Prometheus/Grafana**
- [ ] Logs estruturados (JSON) e monitoramento centralizado
- [ ] Deploy em nuvem (Render/Heroku/DigitalOcean)

---

## 🤝 Contribuição

Contribuições são bem-vindas!  
Se você quiser sugerir melhorias, abrir issues ou enviar PRs, fique à vontade.  

Este projeto segue o padrão de commits **Conventional Commits** para manter histórico limpo e organizado.

### 📌 Padrão de Commits

Use o formato:

### 🔹 Exemplos

- `feat(ingestao): adicionar endpoint para upload de JSON com JWT`
- `fix(distribuicao): corrigir bug no consumo de mensagens da fila processed_data`
- `docs(readme): adicionar diagrama da arquitetura`
- `chore(ci): configurar GitHub Actions para rodar testes`

### 🔹 Tipos mais usados

- **feat** → nova funcionalidade  
- **fix** → correção de bug  
- **docs** → documentação  
- **style** → mudanças de formatação/código sem impacto funcional  
- **refactor** → refatoração de código sem mudar funcionalidade  
- **test** → adição/correção de testes  
- **chore** → manutenção/infraestrutura  

---

## 📄 Licença

Este projeto está licenciado sob a licença **MIT** – veja o arquivo [LICENSE](LICENSE) para mais detalhes.  
Sinta-se livre para usar, modificar e compartilhar, mantendo a referência ao autor.

---

## 👨‍💻 Autor

Desenvolvido por **Thiago Povoa**  

- 🌐 [Em breve](https://github.com/devpovoa)
- 💼 [LinkedIn](https://www.linkedin.com/in/thiago-povoa-dev)  
- 🐙 [GitHub](https://github.com/devpovoa)  

---

## 🙏 Agradecimentos

Um agradecimento especial ao meu mentor **Ricardo Fernandes** pelo direcionamento técnico, feedbacks francos e suporte contínuo durante essa minha trajetória.  

- 💼 [LinkedIn — José Ricardo Fernandes](https://www.linkedin.com/in/jose-ricardo-fernandes/)


