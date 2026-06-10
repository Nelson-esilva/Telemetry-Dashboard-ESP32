# Projeto de Telemetria de Produção

Sistema acadêmico que simula telemetria industrial: um **ESP32** envia dados via HTTP para uma **API FastAPI**, que grava em **SQLite**; um **dashboard Streamlit** exibe as métricas em tempo quase real.

## Arquitetura

```
ESP32 (firmware)  --HTTP POST-->  FastAPI  -->  SQLite  <--  Streamlit
```

## Pré-requisitos

- Python 3.10+
- PlatformIO (para gravar o firmware no ESP32)
- ESP32 e PC na mesma rede WiFi

## Instalação

```bash
cd /home/nelson/Projetos/UEA/Microcontroladores
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 1. Subir a API

```bash
# Na raiz do projeto, com o venv ativado
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Verifique: [http://localhost:8000/health](http://localhost:8000/health)

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

## 2. Rodar o dashboard

Em outro terminal:

```bash
source .venv/bin/activate
streamlit run dashboard/app.py
```

O dashboard atualiza automaticamente a cada 5 segundos.

## 3. Configurar e gravar o firmware ESP32

1. Copie o arquivo de configuração:

```bash
cp firmware/include/config.example.h firmware/include/config.h
```

2. Edite `firmware/include/config.h` com:
   - SSID e senha da sua rede WiFi
   - IP local do PC (não use `localhost`) — descubra com `ip addr` ou `hostname -I`
   - Porta da API (padrão: `8000`)

3. Grave no ESP32 com PlatformIO:

```bash
cd firmware
pio run -t upload
pio device monitor
```

## 4. Simular sem hardware (opcional)

Útil para demonstração em sala de aula sem ESP32 conectado:

```bash
python scripts/simulate_esp.py
```

## Estrutura do projeto

```
Microcontroladores/
├── backend/           # API FastAPI
├── dashboard/         # App Streamlit
├── firmware/          # Projeto PlatformIO (ESP32)
├── scripts/           # Simulador de ESP
├── telemetry.db       # Banco SQLite (criado ao subir a API)
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

- **ESP não conecta à API:** confirme que PC e ESP estão na mesma rede e que o IP em `config.h` está correto.
- **Firewall bloqueando:** no Linux, libere a porta 8000 com `sudo ufw allow 8000`.
- **Dashboard vazio:** certifique-se de que a API está recebendo dados (via ESP ou `simulate_esp.py`).
