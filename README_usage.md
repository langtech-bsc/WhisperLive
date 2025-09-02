# STEPS

This steps have been tested in the innovation machine (\*.\*.\*.151).

## Review configuration

The configuration is the result of loading environment variables and default values. These can be found in:
- `WhisperLive/.env` file for environment variables 
- `app/config.py` which loads the former ones and contains the default ones as well

## Docker tests

### 1. Run docker compose

```
cd WhisperLive
docker compose up --build
```

### 2. Start Kafka consumer:

```
cd WhisperLive
source .venv/bin/activate
python3 examples/kafka/consumer.py
```

### 3. Call FastAPI endpoint by streaming audio file and sending results in realtime to kafka:

```
cd WhisperLive
source .venv/bin/activate
python3 examples/api/process_file_requests.py
```



## Local tests

### 1. Load model in innovation machine: 
```
cd WhisperLive
source .venv/bin/activate
python3 run_server.py --port 9090 --backend faster_whisper --cache_path /home/marti/.cache/huggingface/hub/
```

### 2. Start FastAPI server (laptop): 

```
cd WhisperLive
source .venv/bin/activate
fastapi dev app/main.py
```

### 3. Start Kafka consumer:

```
cd WhisperLive
source .venv/bin/activate
python3 examples/kafka/consumer.py
```

### 4. Call FastAPI endpoint by streaming audio file and sending results in realtime to kafka:

```
cd WhisperLive
source .venv/bin/activate
python3 examples/api/process_file_requests.py
```