# Real-time ASR evaluation

The aim is to evaluate the degradation in terms of the transcription WER by comparing 2 transcriptions: whole file vs real-time.

## Main steps

What is necessary to do the evaluation, these steps are run in the following order:
- list files to evaluate, save as a text file.
- run the transcription of complete files. The result is taken as groundtruth.
- run the transcription by simulating real time scenario. The result is taken to measure the degradation wrt groundtruth.
- take both transcriptions and measure WER. WER and CER are computed using the [jiwer](https://github.com/jitsi/jiwer) library, after lowercasing and stripping punctuation.
- the same experiment is run with multiple models, e.g. tiny, large-v2

Some clarifications:
- The evaluation code resides under evaluation/ within the main WhisperLive repo
- there is no such full file WER and real-time WER. There is a single WER metric that uses the full file transcript as groundtruth, and the real-time transcription is compared against it to compute the WER and CER. There are no manual transcriptions.

## How to run it?

### Launch the ASR and FastAPI servers

This are the 2 commands to launch these servers, configure accordingly:

- To launch the ASR server:

    ```bash
    docker run -v cache:/cache -e HF_HOME="/cache/" -it -p 9090:9090 ghcr.io/collabora/whisperlive-cpu:latest python run_server.py -c /cache
    ```

- To launch the FastAPI server:

    ```bash
    uvicorn app.main:app --host 0.0.0.0 --port 8052 --reload
    ```

### Call example

Run this code as in the following example:

```bash
python -m evaluation.src.evaluate_asr --config evaluation/config/eval_dataset_1.yaml
```

### YAML configuration file

Example of the yaml file:

```yaml
---
data:
  file_list: /path/to/filelist.txt
metrics:
  error: ["wer", "cer"]
  metadata: ["duration"]
models: ["tiny", "large-v2"]
steps:                              # in order to control what is done in the current execution
  do_full_file_transcription: true
  do_real_time_transcription: true
  do_compute_metrics: true
  do_plots: true
output:
  folder: results/
```

YAML configuration files are stored under:

```bash
evaluation/config/
└── eval_dataset_1.yaml             # filename is used to create a results sub-folder
```

### Results folder

Results are stored in a folder structure like:

```bash
evaluation/results/
└── eval_dataset_1                  # folder with the same name as the config file
    ├── eval_dataset_1.yaml         # a copy of the configuration file used to facilitat reproducibility
    ├── metadata
    │   └── metadata.json           # JSON file with wav files IDs and some metadata like file duration
    ├── metrics                     # metrics subfolder
    │   ├── large-v2.json           # metrics like WER, CER for large-v2 model
    │   └── tiny.json               # metrics like WER, CER for tiny model
    ├── plots                       # plots subfolder
    │   ├── cer_duration.png        # plot CER (y axis) vs file duration (x axis)
    │   └── wer_duration.png        # plot WER (y axis) vs file duration (x axis)
    ├── summary.csv                 # CSV file summarizing the evaluation run
    └── transcriptions              # transcriptions subfolder
        ├── full                    # transcriptions when the full file was used
        │   ├── large-v2.json       #   each file ID has the full file transcription with the large-v2 model
        │   └── tiny.json           #   each file ID has the full file transcription with the tiny model
        └── real_time               # transcriptions when the real-time scenario was simulated
            ├── large-v2.json       #   each file ID has the real-time transcription with the large-v2 model
            └── tiny.json           #   each file ID has the real-time transcription with the tiny model
```

### File list format

A simple text file where each line contains the full path to a single WAV file:

```bash
/data/audio/sample1.wav
/data/audio/sample2.wav
...

```

### Results files

Both full and real-time transcription output json files contain a list of dictionaries, where each one is something like:

```json
[
    {
        "wav": "/path/to/file/1234.wav",
        "ID": "1234",
        "asr": [
            {
                "start": 0,
                "end": "1.1",
                "text": "hello world, how are you?"
            },
            {
                "start": 1.8,
                "end": "3",
                "text": "This Charles me speaking, who are you?"
            }
        ],
        "transcript": "hello world, how are you? This Charles me speaking, who are you?"
    },
    {
        "wav": "/path/to/file/sdfgsdg.wav",
        "ID": "sdfsf",
        "asr": [
            {
                "start": 0.1,
                "end": "2.1",
                "text": "one two three four"
            },
            {
                "start": 2.8,
                "end": "4",
                "text": "five six seven eigth"
            }
        ],
        "transcript": "one two three four five six seven eigth"
    }
]
```

Metrics JSON files have the following format:

```json
[
    {
        "wav": "/path/to/file/1234.wav",
        "wer": 0.75,
        "cer": 0.8
    },
    {
        "wav": "/path/to/file/sdfgsdg.wav",
        "wer": 0.55,
        "cer": 0.63
    }
]
```

Metadata JSON files have the following format, where duration is expressed in seconds:

```json
[
    {
        "wav": "/path/to/file/1234.wav",
        "duration": 33.5,
    },
    {
        "wav": "/path/to/file/sdfgsdg.wav",
        "duration": 62.6,
    }
]
```

Plots are matplotlib scatterplots of X = file durations and Y = WER or CER depending on the file.


### Get file transcription from the full file

As described here https://huggingface.co/Systran/faster-whisper-large-v2, a function implements this part:

```python
from faster_whisper import WhisperModel

model = WhisperModel("large-v2")

segments, info = model.transcribe("audio.wav")
for segment in segments:
    print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
```

### Get the file transcription simulating real-time scenario

It uses a similar approach to the example file in examples/client/launch_client_from_file.py

```python
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

  # language = "es"
  wav_file = "/path/to/file.wav"
  language = "es"
  model = "large-v2" 
  server_IP = "84.88.51.151" # "localhost"

  client_from_file(server_IP = server_IP, 
                   wav_file = wav_file, 
                   language = language, 
                   model = model,
                   transcription_callback = None,
                   mute_audio_playback = True)
```


### Summary CSV file format

A `summary.csv` file is automatically generated in the corresponding results folder. It aggregates per-file metrics across models and computes global averages (mean WER/CER, number of files, and average duration). For example:

| model    | avg_WER | avg_CER | num_files | avg_duration |
| -------- | ------- | ------- | --------- | ------------ |
| tiny     | 0.42    | 0.31    | 120       | 34.5         |
| large-v2 | 0.21    | 0.18    | 120       | 34.5         |

## Code structure

The code is organized as follows:
- evaluate_asr.py is the main script which takes the config YAML file as input and imports all other python files

```bash
tree evaluation/src/

evaluation/src/
├── compute_metrics.py
├── evaluate_asr.py
├── io_utils.py                     # YAML, JSON, CSV I/O helpers
├── plot_results.py
├── run_full_transcription.py
└── run_realtime_transcription.py
```

## Pending:

- Add latency metrics (mean segment delay) for real-time runs.
- Support additional metadata: CPU/GPU usage, transcription time, etc.
- Extend YAML schema with realtime settings (chunk size, buffer time, etc.).