import requests
import uuid

def generate_input_id(type="random"):
    """Generate a unique input ID."""
    if type == "random":
        return str(uuid.uuid4())
    elif type == "fixed":
        return "447ad06b-6efa-423f-b1d1-df5673dc9db0"

def get_segments(amount=1):

    segments = [
                {"text": "Hello", "start": 0.0, "end": 1.0},
                {"text": "world!", "start": 1.0, "end": 2.0},
                {"text": "Hola!", "start": 2.0, "end": 3.0},
                {"text": "mon!", "start": 3.0, "end": 4.0},
            ]
    
    return segments[:amount]

def main(idx=1):
    url = "http://127.0.0.1:8052/send_kafka_message"
    segments = get_segments(amount=idx)
    print(f"Sending {len(segments)} segments")
    print(f"Segments: {segments}")
    payload = {
        "session_id": generate_input_id(type="fixed"),
        "full_transcript": "\n".join([f"{seg['start']} {seg['end']} {seg['text']}" for seg in segments]),
        "segments": segments,
    }
    print(f"payload: {payload}")

    r = requests.post(url, json=payload)
    print(r.json())

if __name__ == "__main__":
    for idx in range(4):
        print("\n--- Iteration", idx+1, "---")
        main(idx=idx+1)
