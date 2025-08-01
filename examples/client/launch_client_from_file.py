from whisper_live.client import TranscriptionClient

def client_from_file(wav_file, server_IP = "84.88.51.151", port = "9090", language="es", model="tiny", 
                     transcription_callback = None, mute_audio_playback = False):
  """ Launches the transcription client with a file input.
  """

  client = TranscriptionClient(
    server_IP,
    port,
    lang=language,
    translate=False,
    model = model,
    use_vad=True,
    mute_audio_playback=mute_audio_playback,                          # Only used for file input, False by Default
    transcription_callback = transcription_callback
  )
  client(wav_file)

if __name__ == "__main__":

  # wav_file = "/home/mumbert/Documentos/BSC/projects/s2st_dataset/tests/data/wav/rXn1vkhUZZk_chunk_300s.wav"
  # language = "ca"
  # wav_file = "/home/mumbert/Documentos/BSC/projects/langtech-bsc/innovation-renfe-dev/renfe/gpfs/projects/bsc88/renfe/safe_recordings/129b7905-a9f4-4c66-9fff-d5c37acf7a49.WAV"
  wav_file = "/home/mumbert/Descargas/RENFE_logs/audios/1cd8983e-f38b-4df6-9510-7b973e006a17_only_conversation.wav"
  language = "es"
  model = "tiny" 
  server_IP = "84.88.51.151" # "localhost"

  client_from_file(server_IP = server_IP, 
                   wav_file = wav_file, 
                   language = language, 
                   model = model,
                   transcription_callback = None)


