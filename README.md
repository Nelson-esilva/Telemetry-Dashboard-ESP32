# Projeto de Telemetria de Produção

Sistema acadêmico que simula telemetria industrial: um **ESP32** envia dados via HTTP para uma **API FastAPI**, que grava em **SQLite**; um **dashboard Streamlit** exibe as métricas em tempo quase real.

## Arquitetura

```
ESP32 (firmware)  --HTTP POST-->  FastAPI  -->  SQLite  <--  Streamlit
```

O ESP32 gera dados simulados (temperatura, RPM, status da máquina, etc.) a cada 5 segundos e envia para a API. O dashboard lê o banco diretamente e atualiza os gráficos automaticamente.

## Pré-requisitos

- Python 3.10+
- PlatformIO (extensão no VS Code/Cursor ou `pip install platformio`)
- Placa ESP32 (testado com **ESP32-S2**)
- PC e ESP32 na mesma rede local (Wi-Fi ou Ethernet no mesmo roteador)

## Instalação

### Windows (PowerShell)

```powershell
cd Telemetry-Dashboard-ESP32
python -m venv ..\.venv
..\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Linux / macOS

```bash
cd Telemetry-Dashboard-ESP32
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Como rodar

São necessários **3 terminais** (com o venv ativado na raiz do repositório):

### 1. Subir a API

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Verifique: [http://localhost:8000/health](http://localhost:8000/health) → `{"status":"ok"}`

Documentação interativa: [http://localhost:8000/docs](http://localhost:8000/docs)

Teste manual com curl:

```bash
curl -X POST http://localhost:8000/telemetry \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "linha_01",
    "pecas_produzidas": 10,
    "temperatura_c": 45.2,
    "rpm_motor": 1200,
    "status_maquina": "RUNNING",
    "tempo_ciclo_s": 2.5,
    "eficiencia_pct": 92.0
  }'
```

### 2. Rodar o dashboard

```bash
streamlit run dashboard/app.py
```

O dashboard abre em [http://localhost:8501](http://localhost:8501) e atualiza a cada 5 segundos.

**Recursos do dashboard:**
- Cards com métricas em tempo quase real
- Gráficos de temperatura, RPM e eficiência
- Filtro por período: último minuto, últimos 5 minutos ou todos os registros
- Quebra automática de linha quando o ESP para de enviar dados
- Alerta visual quando a máquina está em estado `ALARM`

### 3. Enviar telemetria

**Opção A — ESP32 físico** (veja seção de firmware abaixo)

**Opção B — Simulador sem hardware:**

```bash
python scripts/simulate_esp.py
```

## Firmware ESP32

### 1. Instalar PlatformIO

**Via extensão (recomendado):** instale **PlatformIO IDE** no VS Code ou Cursor.

**Via pip:**

```bash
pip install platformio
```

> Pare a API (`uvicorn`) antes de instalar pacotes no mesmo venv, para evitar conflito de arquivos no Windows.

### 2. Driver USB (Windows)

Se o ESP32 não aparecer como porta COM no Gerenciador de Dispositivos:

| Chip USB | Driver |
|----------|--------|
| CP2102 / CP2102N | [Silicon Labs CP210x](https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers) |
| CH340 / CH341 | [Driver CH340](https://www.wch-ic.com/downloads/CH341SER_EXE.html) |

Após instalar, o dispositivo deve aparecer em **Portas (COM e LPT)**, por exemplo: `Silicon Labs CP210x (COM3)`.

### 3. Configurar credenciais

```bash
cp firmware/include/config.example.h firmware/include/config.h
```

Edite `firmware/include/config.h`:

| Campo | Descrição |
|-------|-----------|
| `WIFI_SSID` | Nome da rede Wi-Fi |
| `WIFI_PASSWORD` | Senha da rede |
| `API_HOST` | IP local do PC na rede (não use `localhost`) |
| `API_PORT` | Porta da API (padrão: `8000`) |
| `DEVICE_ID` | Identificador da linha (ex.: `linha_01`) |

**Descobrir o IP do PC:**

```powershell
# Windows
ipconfig
```

```bash
# Linux
ip addr
hostname -I
```

> PC conectado por **Ethernet** e ESP32 por **Wi-Fi** funciona normalmente, desde que estejam no mesmo roteador (não use rede convidado/guest).

### 4. Compilar e gravar

O projeto está configurado para **ESP32-S2**. Se sua placa for ESP32 clássico, altere `board` em `firmware/platformio.ini` para `esp32dev`.

```bash
cd firmware
pio device list          # descubra a porta COM
pio run -t upload --upload-port COM3
pio device monitor
```

Se o upload falhar, segure **BOOT**, pressione **RESET**, solte **BOOT** e tente novamente.

## Estrutura do projeto

```
Telemetry-Dashboard-ESP32/
├── backend/              # API FastAPI
│   ├── main.py           # Rotas HTTP
│   ├── models.py         # Validação Pydantic
│   └── database.py       # SQLite + SQLAlchemy
├── dashboard/
│   └── app.py            # Dashboard Streamlit
├── firmware/             # Projeto PlatformIO (ESP32-S2)
│   ├── src/main.cpp
│   ├── include/config.example.h
│   └── platformio.ini
├── scripts/
│   └── simulate_esp.py   # Simulador de telemetria
├── telemetry.db          # Banco SQLite (criado ao subir a API)
└── requirements.txt
```

## Campos de telemetria

| Campo | Descrição |
|-------|-----------|
| `device_id` | Identificador da linha (ex.: `linha_01`) |
| `pecas_produzidas` | Contador acumulado de peças |
| `temperatura_c` | Temperatura simulada (°C) |
| `rpm_motor` | Rotação do motor (RPM) |
| `status_maquina` | `RUNNING`, `IDLE` ou `ALARM` |
| `tempo_ciclo_s` | Duração do ciclo de produção (s) |
| `eficiencia_pct` | Eficiência simulada (%) |

## Solução de problemas

| Problema | Solução |
|----------|---------|
| ESP não aparece no `pio device list` | Instale o driver USB (CP210x ou CH340) |
| `ESP32-S2, not ESP32` no upload | Placa é S2 — use `board = esp32-s2-saola-1` no `platformio.ini` |
| `WIFI_SSID was not declared` | Crie `config.h` a partir de `config.example.h` |
| ESP não conecta à API | Confirme IP em `config.h`, mesma rede e API com `--host 0.0.0.0` |
| Firewall bloqueando | Libere a porta 8000 no Windows/Linux |
| Dashboard vazio | API rodando e ESP/simulador enviando dados |
| Gráfico com linha estranha | Use o filtro de tempo ou aguarde — lacunas > 20s quebram a linha automaticamente |
| Erro ao `pip install` no Windows | Pare o `uvicorn` antes de instalar pacotes no venv |

## Tecnologias

- **Firmware:** C++ / Arduino / PlatformIO
- **Backend:** Python / FastAPI / SQLAlchemy / SQLite / Pydantic
- **Dashboard:** Python / Streamlit / Plotly / Pandas
