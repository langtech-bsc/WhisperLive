# https://huggingface.co/docs/huggingface_hub/en/guides/inference_endpoints#get-or-list-existing-inference-endpoints

from huggingface_hub import get_inference_endpoint, list_inference_endpoints

# get_inference_endpoint("my-endpoint-name")

def get_inference_endpoints(organization: str = "BSC-LT"):
    ie = list_inference_endpoints(namespace=organization)
    for id, endpoint in enumerate(ie):
        print(f"({id+1}/{len(ie)})\tname: {endpoint.name}\tstatus: {endpoint.status}\trepository: {endpoint.repository}")

if __name__ == "__main__":
    for org in ["BSC-LT", "langtech-innovation"]:
        print(f"\nListing endpoints for organization: {org}")
        get_inference_endpoints(organization=org)