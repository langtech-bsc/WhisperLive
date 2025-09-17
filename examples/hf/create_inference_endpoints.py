import os
from dotenv import load_dotenv
from huggingface_hub import create_inference_endpoint
import yaml

##########
# https://huggingface.co/docs/huggingface_hub/en/guides/inference_endpoints#using-a-custom-image
# dashboard: https://endpoints.huggingface.co/


def load_env_file_config():

    load_dotenv()

    global ASR_SERVER, ASR_PORT, ASR_MODEL, ASR_LANGUAGE, ASR_MUTE_AUDIO_PLAYBACK
    global FASTAPI_SERVER, FASTAPI_PORT
    global DO_PRINT_KAFKA_MESSAGES, DO_SEND_KAFKA_MESSAGES
    global KAFKA_SERVER, KAFKA_PORT, KAFKA_TOPIC

    # ASR
    ASR_SERVER = os.getenv("ASR_SERVER", "None")
    ASR_PORT = os.getenv("ASR_PORT", "None")
    ASR_MODEL = os.getenv("ASR_MODEL", "None")
    ASR_LANGUAGE = os.getenv("ASR_LANGUAGE", "None")
    ASR_MUTE_AUDIO_PLAYBACK = os.getenv("ASR_MUTE_AUDIO_PLAYBACK", "False").lower() == 'true'

    # FASTAPI
    FASTAPI_SERVER = os.getenv("FASTAPI_SERVER", "None")
    FASTAPI_PORT = os.getenv("FASTAPI_PORT", "None")

    # KAFKA
    KAFKA_SERVER = os.getenv("KAFKA_SERVER", "None")
    KAFKA_PORT = os.getenv("KAFKA_PORT", "None")
    KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "None")
    DO_PRINT_KAFKA_MESSAGES = os.getenv("DO_PRINT_KAFKA_MESSAGES", "False").lower() == 'true'
    DO_SEND_KAFKA_MESSAGES = os.getenv("DO_SEND_KAFKA_MESSAGES", "False").lower() == 'true'

def load_yaml_config(yaml_file: str = "config.yaml"):
    """Loads configuration variables from a YAML file."""

    global INFERENCE_ENDPOINT_NAME
    global REPOSITOY
    global FRAMEWORK
    global TASK
    global ACCELERATOR
    global VENDOR
    global REGION
    global TYPE
    global INSTANCE_SIZE
    global INSTANCE_TYPE
    global CUSTOM_IMAGE_URL

    if not os.path.exists(yaml_file):
        print(f"ERROR: YAML config file '{yaml_file}' not found. Exiting...")
        exit(1)

    with open(yaml_file, 'r') as file:
        config = yaml.safe_load(file)

    INFERENCE_ENDPOINT_NAME = config.get("INFERENCE_ENDPOINT_NAME", None)
    REPOSITOY = config.get("REPOSITOY", None)
    FRAMEWORK = config.get("FRAMEWORK", None)
    TASK = config.get("TASK", None)
    ACCELERATOR = config.get("ACCELERATOR", None)
    VENDOR = config.get("VENDOR", None)
    REGION = config.get("REGION", None)
    TYPE = config.get("TYPE", None)
    INSTANCE_SIZE = config.get("INSTANCE_SIZE", None)
    INSTANCE_TYPE = config.get("INSTANCE_TYPE", None)
    CUSTOM_IMAGE_URL = config.get("CUSTOM_IMAGE_URL", None)

def load_config_variables(yaml_file: str = "config.yaml"):

    load_env_file_config()
    load_yaml_config(yaml_file=yaml_file)
    
def show_config():

    print("\n* Configuration Variables from enviroment:")

    print(f"ASR_SERVER: {ASR_SERVER}")
    print(f"ASR_PORT: {ASR_PORT}")
    print(f"ASR_MODEL: {ASR_MODEL}")
    print(f"ASR_LANGUAGE: {ASR_LANGUAGE}")
    print(f"ASR_MUTE_AUDIO_PLAYBACK: {ASR_MUTE_AUDIO_PLAYBACK}")

    print(f"FASTAPI_SERVER: {FASTAPI_SERVER}")
    print(f"FASTAPI_PORT: {FASTAPI_PORT}")

    print(f"KAFKA_SERVER: {KAFKA_SERVER}")
    print(f"KAFKA_PORT: {KAFKA_PORT}")
    print(f"KAFKA_TOPIC: {KAFKA_TOPIC}")
    print(f"DO_PRINT_KAFKA_MESSAGES: {DO_PRINT_KAFKA_MESSAGES}")
    print(f"DO_SEND_KAFKA_MESSAGES: {DO_SEND_KAFKA_MESSAGES}")

    print("\n* Configuration Variables from YAML file:")

    print(f"INFERENCE_ENDPOINT_NAME: {INFERENCE_ENDPOINT_NAME}")
    print(f"REPOSITOY: {REPOSITOY}")
    print(f"FRAMEWORK: {FRAMEWORK}")
    print(f"TASK: {TASK}")
    print(f"ACCELERATOR: {ACCELERATOR}")
    print(f"VENDOR: {VENDOR}")
    print(f"REGION: {REGION}")
    print(f"TYPE: {TYPE}")
    print(f"INSTANCE_SIZE: {INSTANCE_SIZE}")
    print(f"INSTANCE_TYPE: {INSTANCE_TYPE}")
    print(f"CUSTOM_IMAGE_URL: {CUSTOM_IMAGE_URL}")

def create_hf_inference_endpoint():

    pass    

    # endpoint = create_inference_endpoint(
    #     name = INFERENCE_ENDPOINT_NAME,
    #     repository = REPOSITORY,
    #     framework = FRAMEWORK,
    #     task = TASK,
    #     accelerator = ACCELERATOR,
    #     vendor = VENDOR,
    #     region = REGION,
    #     type = TYPE,
    #     instance_size = INSTANCE_SIZE,
    #     instance_type = INSTANCE_TYPE,
    #     custom_image={
    #         "health_route": "/health",
    #         "env": {
    #             "MAX_BATCH_PREFILL_TOKENS": "2048",
    #             "MAX_INPUT_LENGTH": "1024",
    #             "MAX_TOTAL_TOKENS": "1512",
    #             "MODEL_ID": "/repository"
    #         },
    #         "url": CUSTOM_IMAGE_URL,
    #     },
    # )

    # print("Endpoint created:", endpoint.url)

def main(yaml_file: str = "config.yaml"):

    load_config_variables(yaml_file=yaml_file)
    show_config()
    create_hf_inference_endpoint()

if __name__ == "__main__":

    # use argparse to get a yaml file path from command line (it will be used to load config variables)
    # the name of the argument should be yaml_file
    import argparse
    parser = argparse.ArgumentParser(description="Create HF Inference Endpoint")
    parser.add_argument('--yaml', type=str, required=False, default="config.yaml", help="Path to the YAML config file")
    args = parser.parse_args()

    main(yaml_file=args.yaml)


    # hf_token = os.getenv("HF_TOKEN")
    # print("HF_TOKEN:", hf_token)


#########################################################
    # endpoint = create_inference_endpoint(
    #     "aws-zephyr-7b-beta-0486",
    #     repository="HuggingFaceH4/zephyr-7b-beta",
    #     framework="pytorch",
    #     task="text-generation",
    #     accelerator="gpu",
    #     vendor="aws",
    #     region="us-east-1",
    #     type="protected",
    #     instance_size="x1",
    #     instance_type="nvidia-a10g",
    #     custom_image={
    #         "health_route": "/health",
    #         "env": {
    #             "MAX_BATCH_PREFILL_TOKENS": "2048",
    #             "MAX_INPUT_LENGTH": "1024",
    #             "MAX_TOTAL_TOKENS": "1512",
    #             "MODEL_ID": "/repository"
    #         },
    #         "url": "ghcr.io/huggingface/text-generation-inference:1.1.0",
    #     },
    # )

    # print("Endpoint created:", endpoint.url)

#########################################################

# from huggingface_hub import InferenceClient, create_inference_endpoint
# import os

# # Authenticate (use your HF token)
# hf_token = os.getenv("HF_TOKEN")

# # Create the endpoint
# endpoint = create_inference_endpoint(
#     name="my-custom-asr-endpoint",
#     # Point to your own image in Docker Hub or another registry
#     custom_image="docker.io/myorg/my-asr:latest",
#     # Optional: environment variables your container needs
#     env={
#         "ASR_MODEL": "tiny",
#         "LANGUAGE": "es"
#     },
#     # Hardware (depends on your image requirements)
#     accelerator="gpu",
#     region="us-east-1",
#     type="public"  # or "private"
# )

# print("Endpoint created:", endpoint.url)