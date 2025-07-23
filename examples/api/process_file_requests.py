import requests

url = "http://localhost:8000/transcribe"
file_path = "/home/mumbert/Descargas/RENFE_logs/audios/1cd8983e-f38b-4df6-9510-7b973e006a17_only_conversation.wav"

with open(file_path, "rb") as audio_file:
    files = {"file": audio_file}
    response = requests.post(url, files=files)

print("Status code:", response.status_code)
print("Response:", response.text)
