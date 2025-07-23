# STEPS
# 1. Load model in innovation machine: 
#   cd WhisperLive
#   source .venv/bin/activate
#   python3 run_server.py --port 9090 --backend faster_whisper --cache_path /home/marti/.cache/huggingface/hub/
# 2. Start FastAPI server (laptop): 
#   cd WhisperLive
#   source .venv/bin/activate
#   fastapi dev app/main.py
# 3. Start Kafka consumer (laptop):
#   cd WhisperLive
#   source .venv/bin/activate
#   python3 examples/kafka/consumer.py
# 4. Call FastAPI endpoint by streaming audio file and sending results in realtime to kafka(laptop):
#   cd WhisperLive
#   source .venv/bin/activate
#   python3 examples/api/process_file_requests.py