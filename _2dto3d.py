import time
import os
import requests
import base64

meshy_api_key = "Your Meshy API Key"

def encode_image_to_base64(image_path):
    """Encode the image to a base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def create_image_to_3d_task(image_path):
    """Create an Image to 3D task in Meshy."""
    headers = {
        "Authorization": f"Bearer {meshy_api_key}",
        "Content-Type": "application/json"
    }

    # Encode the image to base64
    base64_image = encode_image_to_base64(image_path)
    data_uri = f"data:image/jpeg;base64,{base64_image}"

    payload = {
        "image_url": data_uri,
        "ai_model": "meshy-5",
        "should_remesh": True,
        "should_texture": True
    }

    response = requests.post(
        "https://api.meshy.ai/openapi/v1/image-to-3d",
        headers=headers,
        json=payload
    )

    response.raise_for_status()
    return response.json()["result"]

def retrieve_task_status(task_id):
    """Retrieve the status of the Image to 3D task."""
    headers = {
        "Authorization": f"Bearer {meshy_api_key}"
    }

    response = requests.get(
        f"https://api.meshy.ai/openapi/v1/image-to-3d/{task_id}",
        headers=headers
    )

    response.raise_for_status()
    return response.json()

def download_model(model_url, output_path):
    """Download the generated 3D model."""
    response = requests.get(model_url)
    response.raise_for_status()

    with open(output_path, "wb") as file:
        file.write(response.content)

def img_to_3d(image_path, output_dir):
    """Main function to convert a 2D image to a 3D model."""
    task_id = create_image_to_3d_task(image_path)
    print(f"Task created with ID: {task_id}")

    # Polling the task status
    while True:
        task_status = retrieve_task_status(task_id)
        status = task_status["status"]
        progress = task_status.get("progress", 0)
        print(f"Task Status: {status}, Progress: {progress}%")

        if status == "SUCCEEDED":
            model_url = task_status["model_urls"]["glb"]
            output_path = os.path.join(output_dir, f"{task_id}.glb")
            download_model(model_url, output_path)
            print(f"Model downloaded to: {output_path}")
            return output_path
        elif status in ["FAILED", "CANCELLED"]:
            raise Exception(f"Task {status.lower()}.")
        else:
            time.sleep(10)  # Wait before polling again
