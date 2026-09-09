# JARVAS — Assistente Inteligente de Programação

JARVAS é um assistente de programação com chat web (Django), cadastro de usuários, painel administrativo e inteligência artificial local usando o modelo **Qwen2.5-Coder-1.5B-Instruct**.

---

## Índice

1. [Requisitos](#requisitos)
2. [Instalação rápida com Docker](#instalação-rápida-com-docker)
3. [Instalação local (sem Docker)](#instalação-local-sem-docker)
4. [Modos da IA — escolha conforme sua placa de vídeo](#modos-da-ia--escolha-conforme-sua-placa-de-vídeo)
5. [Qual modo usar na minha placa?](#qual-modo-usar-na-minha-placa)
6. [Como usar o sistema](#como-usar-o-sistema)
7. [Acesso administrativo](#acesso-administrativo)
8. [Variáveis de ambiente](#variáveis-de-ambiente)
9. [Solução de problemas](#solução-de-problemas)

---

## Requisitos

| Item | Mínimo |
|------|--------|
| Python | 3.10 ou superior |
| MySQL | 8.0 |
| RAM | 8 GB (recomendado 16 GB para IA) |
| Espaço em disco | ~4 GB (modelo + dependências) |
| Placa de vídeo | Opcional (veja seção da IA abaixo) |

**Docker (opcional):** Docker Desktop + Docker Compose

---

## Instalação rápida com Docker

Um único comando sobe o site **e** o banco MySQL:

```bash
docker compose up --build
```

Acesse: **http://localhost:8000**

> **Importante:** dentro do Docker a IA roda em **CPU** por padrão (`JARVAS_IA_DEVICE=cpu`), pois o container não acessa sua placa de vídeo. O site (login, cadastro, admin) funciona normalmente; o chat com IA será mais lento na primeira mensagem (download do modelo).

Para parar:

```bash
docker compose down
```

---

## Instalação local (sem Docker)

### 1. Clone o repositório e entre na pasta

```bash
cd Assistentes-de-Programa-o---Jarvas
```

### 2. Crie um ambiente virtual

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/macOS
```

### 3. Instale as dependências

**Instalação padrão (CPU + NVIDIA se detectada):**

```bash
pip install -r requirements.txt
```

**Se você tem placa AMD (ex.: RX 580) no Windows e quer usar a GPU:**

```bash
pip install -r requirements-directml.txt
```

### 4. Configure o MySQL

Crie o banco de dados:

```sql
CREATE DATABASE IA_JARVAS CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Ajuste usuário/senha em `JARVAS/JARVAS/settings.py` ou use variáveis de ambiente (veja [Variáveis de ambiente](#variáveis-de-ambiente)).

### 5. Rode as migrations e inicie o servidor

```bash
cd JARVAS
python manage.py migrate
python manage.py runserver
```

Acesse: **http://127.0.0.1:8000**

---

## Modos da IA — escolha conforme sua placa de vídeo

A IA do JARVAS pode rodar de **4 formas**. Você escolhe pela variável de ambiente `JARVAS_IA_DEVICE`:

| Modo | Valor | Quando usar |
|------|-------|-------------|
| **Automático** | `auto` | **Padrão.** Detecta sozinho: NVIDIA → AMD (DirectML) → CPU |
| **NVIDIA CUDA** | `cuda` | Placa NVIDIA (GTX, RTX, etc.) com drivers e PyTorch CUDA |
| **AMD DirectML** | `directml` | Placa AMD ou Intel no **Windows** (ex.: RX 580, RX 6600) |
| **Processador** | `cpu` | Qualquer PC, sem GPU ou quando GPU não funciona |

### Como definir o modo

**Windows (PowerShell) — sessão atual:**

```powershell
$env:JARVAS_IA_DEVICE = "cpu"
cd JARVAS
python manage.py runserver
```

**Windows (PowerShell) — RX 580 com DirectML:**

```powershell
$env:JARVAS_IA_DEVICE = "directml"
cd JARVAS
python manage.py runserver
```

**Linux/macOS:**

```bash
export JARVAS_IA_DEVICE=cuda
cd JARVAS && python manage.py runserver
```

**Docker** — já vem configurado em `docker-compose.yml`:

```yaml
JARVAS_IA_DEVICE: cpu
```

Para forçar outro modo no Docker, edite essa linha em `docker-compose.yml` e suba de novo.

### O que acontece em cada modo

```
auto (padrão)
  │
  ├─ NVIDIA detectada?  → usa CUDA (rápido, float16)
  │
  ├─ DirectML instalado? → usa GPU AMD/Intel no Windows
  │
  └─ Nenhuma GPU         → usa CPU (mais lento, mas funciona)
```

Na tela do **chat**, aparece no rodapé qual modo está ativo, por exemplo:

- `IA: ativa — NVIDIA CUDA — GeForce RTX 3060 (auto)`
- `IA: ativa — CPU (nenhuma GPU compatível detectada)`
- `IA: ativa — GPU AMD/Intel — DirectML (auto)`

---

## Qual modo usar na minha placa?

| Placa / Situação | Modo recomendado | Observação |
|------------------|------------------|------------|
| **NVIDIA** (GTX 1060, RTX 2060, RTX 3060…) | `auto` ou `cuda` | Melhor desempenho. Instale [PyTorch com CUDA](https://pytorch.org/get-started/locally/). |
| **AMD RX 580** (Windows) | `directml` | Instale `requirements-directml.txt`. CUDA **não funciona** em AMD. |
| **AMD RX 580** (Linux) | `cpu` | ROCm tem suporte limitado à RX 580; CPU é mais confiável. |
| **Sem placa dedicada** | `cpu` | Funciona, porém respostas demoram mais. |
| **Docker** | `cpu` (já configurado) | Container não enxerga GPU por padrão. |
| **Intel integrada (Windows)** | `directml` | Pode ajudar um pouco; teste com `auto`. |

### RX 580 — passo a passo

1. Instale dependências com DirectML:
   ```bash
   pip install -r requirements-directml.txt
   ```
2. Defina o modo antes de iniciar:
   ```powershell
   $env:JARVAS_IA_DEVICE = "directml"
   ```
3. Inicie o servidor:
   ```bash
   cd JARVAS
   python manage.py runserver
   ```
4. Faça login, abra o chat e confira no rodapé se aparece **DirectML**.

Se der erro, use CPU como alternativa garantida:

```powershell
$env:JARVAS_IA_DEVICE = "cpu"
```

---

## Como usar o sistema

### Usuário comum

1. Acesse **http://localhost:8000/login/**
2. Clique em **Criar conta** (`/cadastro/`) ou faça login
3. Use o **chat** para perguntas de programação

### URLs principais

| Página | URL |
|--------|-----|
| Login | `/login/` |
| Cadastro | `/cadastro/` |
| Chat | `/chat/` |
| Admin | `/painel/login/` |

---

## Acesso administrativo

Administradores **não** se cadastram pela tela normal. Use o painel separado:

1. Acesse **http://localhost:8000/painel/login/**
2. Credenciais padrão (criadas automaticamente na migration):

| Campo | Valor |
|-------|-------|
| E-mail | `fl2646730@gmail.com` |
| Senha | `12345678` |

3. No painel você pode:
   - Ver estatísticas do sistema
   - Criar, editar e desativar usuários
   - Criar outros administradores
   - Alterar sua senha em **Meu perfil**

> **Segurança:** altere a senha padrão em produção.

---

## Variáveis de ambiente

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `JARVAS_IA_DEVICE` | `auto` | Modo da IA: `auto`, `cuda`, `cpu`, `directml` |
| `JARVAS_IA_MODELO` | `Qwen/Qwen2.5-Coder-1.5B-Instruct` | Modelo Hugging Face |
| `DB_HOST` | `localhost` | Host do MySQL |
| `DB_PORT` | `3306` | Porta do MySQL |
| `DB_USER` | `root` | Usuário do MySQL |
| `DB_PASSWORD` | `12345` | Senha do MySQL |
| `DB_NAME` | `IA_JARVAS` | Nome do banco |
| `DEBUG` | `True` | Modo debug Django |
| `ALLOWED_HOSTS` | `127.0.0.1,localhost,...` | Hosts permitidos |
| `SECRET_KEY` | (valor dev) | Chave secreta Django |

---

## Solução de problemas

### `CUDA não está disponível`

Você tem placa **AMD** ou não instalou PyTorch com CUDA. Use:

```powershell
$env:JARVAS_IA_DEVICE = "cpu"
```

Ou, no Windows com AMD:

```powershell
pip install -r requirements-directml.txt
$env:JARVAS_IA_DEVICE = "directml"
```

### Chat lento na primeira mensagem

Normal. O modelo (~3 GB) é baixado na primeira pergunta. Depois fica em cache.

### Erro de conexão com MySQL

- Verifique se o MySQL está rodando
- Confira `DB_HOST`, `DB_USER`, `DB_PASSWORD` e `DB_NAME`
- No Docker, aguarde o container `db` ficar saudável antes do `web`

### IA indisponível no chat

A mensagem de erro aparece no topo da tela. Confira:

1. Dependências instaladas (`pip install -r requirements.txt`)
2. Modo correto para sua placa (`JARVAS_IA_DEVICE`)
3. Logs no terminal onde o `runserver` está rodando

### Docker não usa minha placa NVIDIA

Por padrão o Docker usa CPU. Passar GPU NVIDIA para Docker exige [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) e configuração extra — para desenvolvimento, rodar **fora do Docker** com `JARVAS_IA_DEVICE=cuda` é mais simples.

---

## Estrutura do projeto

```
Assistentes-de-Programa-o---Jarvas/
├── InteligenciaArtificial.py   # IA — detecta GPU/CPU automaticamente
├── requirements.txt            # Dependências principais
├── requirements-directml.txt   # Extra para AMD no Windows
├── Dockerfile
├── docker-compose.yml
├── docker/entrypoint.sh
└── JARVAS/
    ├── manage.py
    └── APP/                    # App Django (views, models, templates)
```

---

## Licença e créditos

Modelo de IA: [Qwen/Qwen2.5-Coder-1.5B-Instruct](https://huggingface.co/Qwen/Qwen2.5-Coder-1.5B-Instruct) (Hugging Face)
