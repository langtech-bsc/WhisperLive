from whisper_live.client import TranscriptionClient

language = "ca"
model = "large-v3"
server_IP = "84.88.51.151" # "localhost"

client = TranscriptionClient(
  server_IP,
  9090,
  lang=language,
  translate=False,
  model=model,                                      # also support hf_model => `Systran/faster-whisper-small`
  use_vad=False,
  save_output_recording=True,                         # Only used for microphone input, False by Default
  output_recording_filename="./output_recording.wav", # Only used for microphone input
  mute_audio_playback=False,                          # Only used for file input, False by Default
)

client()  # Start the client to listen for microphone input