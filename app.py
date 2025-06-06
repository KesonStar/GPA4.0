from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
import _1dto1d as gpt_4_api
import _2dto3d as meshy_api  # Import the Meshy API module
import os
import datetime  # Add datetime import
import base64
from io import BytesIO
import shutil
from dotenv import load_dotenv
from openai import OpenAI
from google import genai
from google.genai import types
from PIL import Image

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize conversation states
appearance_conversation = None
commercial_conversation = None
appearance_summary = ""
commercial_summary = ""
product_introduction = ""
current_phase = 0
session_save_path = None  # Add global variable for save path

# Initialize API clients
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Global variable to store the current image path
current_image_path = None

# List to store history of image filenames for the current session (for undo)
# This will store just the filenames, not full paths.
# The full path will be constructed using session_save_path + '/2d/' + filename
# However, a simpler approach is to list files in the directory directly.

class Project:
    def __init__(self, timestamp, thumbnail=None, model_filename=None):
        self.timestamp = timestamp
        self.thumbnail = thumbnail
        self.model_filename = model_filename

def get_all_projects():
    projects = []
    models_dir = os.path.join(os.getcwd(), "models")
    
    if not os.path.exists(models_dir):
        return projects
    
    for folder in os.listdir(models_dir):
        folder_path = os.path.join(models_dir, folder)
        if os.path.isdir(folder_path):
            # Check if there's a 2D folder with a Product 2d Image.png
            product_image_path = os.path.join(folder_path, "2d", "Product 2d Image.png")
            
            if os.path.exists(product_image_path):
                # Create thumbnail if it doesn't exist
                thumbnail_name = f"{folder}_thumbnail.png"
                thumbnail_path = os.path.join("static", "project_thumbnails", thumbnail_name)
                
                if not os.path.exists(os.path.join(os.getcwd(), thumbnail_path)):
                    try:
                        with Image.open(product_image_path) as img:
                            img.thumbnail((300, 300))
                            full_thumbnail_path = os.path.join(os.getcwd(), thumbnail_path)
                            img.save(full_thumbnail_path)
                    except Exception as e:
                        print(f"Error creating thumbnail for {folder}: {e}")
                        thumbnail_name = None
                
                # Check if there's a 3D model
                model_filename = None
                model_dir = os.path.join(folder_path, "3d")
                if os.path.exists(model_dir):
                    # Find first .glb file
                    for file in os.listdir(model_dir):
                        if file.endswith(".glb"):
                            # Store full path with timestamp for correct routing
                            model_filename = f"{folder}/3d/{file}"
                            break
                
                projects.append(Project(folder, thumbnail_name, model_filename))
    
    # Sort projects by timestamp (newest first)
    projects.sort(key=lambda x: x.timestamp, reverse=True)
    return projects

@app.route('/dashboard')
def dashboard():
    projects = get_all_projects()
    return render_template('dashboard.html', projects=projects)

@app.route('/')
def home():
    return redirect(url_for('dashboard'))

@app.route('/start-project')
def start_project():
    global current_phase, appearance_conversation, commercial_conversation, appearance_summary, commercial_summary, product_introduction, session_save_path
    # Reset state on page load
    appearance_conversation = gpt_4_api.initialize_appearance_conversation()
    commercial_conversation = gpt_4_api.initialize_commercial_conversation()
    appearance_summary = ""
    commercial_summary = ""
    product_introduction = ""
    current_phase = 1
    
    # Create session-specific save directory
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    session_save_path = os.path.join("models", timestamp)
    os.makedirs(session_save_path, exist_ok=True) # Create the base timestamped directory
    # The '1d' subdirectory will be created by the saving functions
    
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    global appearance_conversation, commercial_conversation, appearance_summary, commercial_summary, product_introduction, current_phase, session_save_path
    
    data = request.json
    user_input = data.get('message', '')
    
    if not user_input:
        return jsonify({"error": "No message provided"}), 400
        
    if session_save_path is None:
        # Should not happen if '/' is called first, but as a safeguard
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        session_save_path = os.path.join("models", timestamp)
        os.makedirs(session_save_path, exist_ok=True)
    
    # Phase 1: Appearance Design
    if current_phase == 1:
        # Check if appearance design is completed
        if user_input.lower() == "appearance design completed":
            # Generate appearance summary
            appearance_summary = gpt_4_api.generate_appearance_summary(appearance_conversation, "User")
            
            # Save appearance conversation and summary to session path
            appearance_conversation_file = gpt_4_api.save_conversation_to_markdown(appearance_conversation, "appearance", session_save_path, "User")
            appearance_summary_file = gpt_4_api.save_summary_to_markdown(appearance_summary, "appearance", session_save_path)
            
            # Move to Phase 2
            current_phase = 2
            
            # Add context from appearance design to commercial conversation
            commercial_conversation.append({
                "role": "user", 
                "content": f"I have completed the appearance design for my product. The appearance design document is as follows:\\n\\n{appearance_summary}\\n\\n \
                    Now I'd like to discuss the commercial application aspects."
            })
            
            # Get AI response to set the context
            ai_response = gpt_4_api.chat_completion(commercial_conversation)
            commercial_conversation.append({"role": "assistant", "content": ai_response})
            
            return jsonify({
                "response": ai_response,
                "phase": current_phase,
                "appearance_summary": appearance_summary,
                "message": "Appearance design phase completed. Moving to commercial application design."
            })
        else:
            # Add user message to appearance conversation
            appearance_conversation.append({"role": "user", "content": user_input})
            
            # Get AI response
            ai_response = gpt_4_api.chat_completion(appearance_conversation)
            
            # Add AI response to conversation
            appearance_conversation.append({"role": "assistant", "content": ai_response})
            
            return jsonify({
                "response": ai_response,
                "phase": current_phase
            })
    
    # Phase 2: Commercial Application Design
    elif current_phase == 2:
        # Check if commercial design is completed
        if user_input.lower() == "commercial application design finished.":
            # Generate commercial summary
            commercial_summary = gpt_4_api.generate_commercial_summary(commercial_conversation, "User")
            
            # Save commercial conversation and summary to session path
            commercial_conversation_file = gpt_4_api.save_conversation_to_markdown(commercial_conversation, "commercial", session_save_path, "User")
            commercial_summary_file = gpt_4_api.save_summary_to_markdown(commercial_summary, "commercial", session_save_path)
            
            # Move to Phase 2.5 (Introduction preparation)
            current_phase = 2.5
            
            return jsonify({
                "response": "Commercial application design phase completed. Type 'Generate Introduction.' to create the final product introduction.",
                "phase": current_phase,
                "commercial_summary": commercial_summary,
                "message": "Commercial application design finished. Ready for product introduction."
            })
        else:
            # Add user message to commercial conversation
            commercial_conversation.append({"role": "user", "content": user_input})
            
            # Get AI response
            ai_response = gpt_4_api.chat_completion(commercial_conversation)
            
            # Add AI response to conversation
            commercial_conversation.append({"role": "assistant", "content": ai_response})
            
            return jsonify({
                "response": ai_response,
                "phase": current_phase
            })
    
    # Phase 2.5: Prepare for Introduction
    elif current_phase == 2.5:
        # Check if user wants to generate the introduction
        if user_input.lower() == "generate introduction.":
            # Move to Phase 3
            current_phase = 3
            
            # Generate product introduction
            product_introduction = gpt_4_api.generate_product_introduction(appearance_summary, commercial_summary, appearance_conversation)
            
            # Save product introduction to session path
            introduction_file = gpt_4_api.save_introduction_to_markdown(product_introduction, session_save_path)
            
            return jsonify({
                "response": "Product introduction generated.", # Kept the change from previous request
                "phase": current_phase,
                "product_introduction": product_introduction,
                "message": "Product design process completed. The final product introduction has been generated."
            })
        else:
            # Just respond without changing state
            return jsonify({
                "response": "Type 'Generate Introduction.' when you're ready to create the final product introduction.",
                "phase": current_phase
            })
    
    # Phase 3: Product Introduction
    elif current_phase == 3:
        # Check if user wants to create an image
        if user_input.lower() == "create image":
            # Move to Phase 4 (Image Generation)
            current_phase = 4
            
            return jsonify({
                "response": "Starting image generation for your product. Please wait while I create the initial image.",
                "phase": current_phase,
                "action": "create_image"
            })
        else:
            return jsonify({
                "response": "The product introduction has been completed. Type 'create image' to generate a 2D image of your product.",
                "phase": current_phase
            })
    
    # Phase 4: Image Generation and Editing
    elif current_phase == 4:
        if user_input.lower() == "image design finished":
            # Final image processing: Set phase to 5 and trigger finalize action
            current_phase = 5
            return jsonify({
                "response": "Processing your final image with higher resolution...",
                "phase": current_phase, # Send phase 5
                "action": "finalize_image"
            })
        # Explicitly check for 'create model' in phase 4 and guide the user
        elif user_input.lower() == "create model":
             return jsonify({
                "response": "Please finalize the image design first by typing 'image design finished'.",
                "phase": current_phase # Stay in phase 4
             })
        else:
            # Any other input in Phase 4 is treated as an edit request
            return jsonify({
                "response": f"Editing the image with your instructions: {user_input}",
                "phase": current_phase, # Stay in phase 4
                "action": "edit_image",
                "edit_prompt": user_input
            })

    # Phase 5: Post-Finalization / 3D Model Creation
    elif current_phase == 5:
        if user_input.lower() == "create model":
            # Correctly trigger model creation in Phase 5
            return jsonify({
                "response": "Starting 3D model generation for your product. Please wait while I create the model.",
                "phase": current_phase, # Stay in phase 5
                "action": "create_model"
            })
        else:
            # Default response for phase 5 if not 'create model'
            return jsonify({
                "response": "Image finalized. Type 'create model' to generate the 3D model.",
                "phase": current_phase # Stay in phase 5
            })

    # If we've gone past all phases (or unexpected state)
    else:
        return jsonify({
            "response": "The product design process has been completed or is in an unexpected state. Refresh the page to start a new design.",
            "phase": current_phase
        })

@app.route('/create-image', methods=['POST'])
def create_image():
    global session_save_path, current_image_path, appearance_summary
    
    # Create 2d directory if it doesn't exist
    image_dir = os.path.join(session_save_path, '2d')
    os.makedirs(image_dir, exist_ok=True)
    
    try:
        # Read appearance design summary for the prompt
        appearance_summary_path = None
        for file in os.listdir(os.path.join(session_save_path, '1d')):
            if file.startswith('appearance_design_summary_'):
                appearance_summary_path = os.path.join(session_save_path, '1d', file)
                break
        
        if appearance_summary_path:
            with open(appearance_summary_path, 'r') as f:
                appearance_design = f.read()
        else:
            appearance_design = appearance_summary  # Use the in-memory version if file not found
        
        # Create prompt for image generation
        prompt = f"There should not be any text in the image. The image should be a single perspective product image. {appearance_design}"
        
        # Call OpenAI to generate image
        result = openai_client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            quality="low"  # Start with low quality for faster generation
        )
        
        image_base64 = result.data[0].b64_json
        image_bytes = base64.b64decode(image_base64)
        
        # Save the image
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        image_filename = f"product_image_{timestamp}.png"
        # current_image_path should store the full path for server-side operations
        current_image_path = os.path.join(image_dir, image_filename)
        
        with open(current_image_path, 'wb') as f:
            f.write(image_bytes)
        
        # Return the image
        return jsonify({
            "success": True,
            "message": "Image created successfully",
            "image_path": f"/get-image/{image_filename}" # Send only filename
        })
    
    except Exception as e:
        print(f"Error creating image: {e}")
        return jsonify({
            "success": False,
            "message": f"Error creating image: {str(e)}"
        }), 500

@app.route('/edit-image', methods=['POST'])
def edit_image():
    global current_image_path, session_save_path
    
    if not current_image_path or not os.path.exists(current_image_path):
        return jsonify({"success": False, "message": "No image exists to edit"}), 400
    
    data = request.json
    prompt = data.get('prompt', '')
    
    if not prompt:
        return jsonify({"success": False, "message": "No edit prompt provided"}), 400
    
    try:
        # Load the current image
        image = Image.open(current_image_path)
        
        # Call Gemini API to edit the image
        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash-preview-image-generation",
            contents=[prompt, image],
            config=types.GenerateContentConfig(
                response_modalities=['TEXT', 'IMAGE']
            )
        )
        
        # Process the response
        image_data = None
        text_response = None
        
        for part in response.candidates[0].content.parts:
            if part.text is not None:
                text_response = part.text
            elif part.inline_data is not None:
                image_data = part.inline_data.data
        
        if image_data:
            # Save the edited image
            image_dir = os.path.join(session_save_path, '2d')
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            image_filename = f"product_image_edited_{timestamp}.png"
            # current_image_path should store the full path
            current_image_path = os.path.join(image_dir, image_filename)
            
            with open(current_image_path, 'wb') as f:
                f.write(image_data)
            
            return jsonify({
                "success": True,
                "message": "Image edited successfully",
                "text_response": text_response or "Image edited based on your instructions.",
                "image_path": f"/get-image/{image_filename}" # Send only filename
            })
        else:
            return jsonify({
                "success": False,
                "message": "No image was generated from the edit"
            }), 500
    
    except Exception as e:
        print(f"Error editing image: {e}")
        return jsonify({
            "success": False,
            "message": f"Error editing image: {str(e)}"
        }), 500

@app.route('/finalize-image', methods=['POST'])
def finalize_image():
    global current_image_path, session_save_path
    
    if not current_image_path or not os.path.exists(current_image_path):
        return jsonify({"success": False, "message": "No image exists to finalize"}), 400
    
    try:
        # Read the current image
        with open(current_image_path, "rb") as image_file:
            # Call OpenAI to generate higher resolution image
            result = openai_client.images.edit(
                model="gpt-image-1",
                image=image_file,
                prompt="Keep the image completely consistent and generate a higher resolution image"
            )
        
        image_base64 = result.data[0].b64_json
        image_bytes = base64.b64decode(image_base64)
        
        # Save the final image
        image_dir = os.path.join(session_save_path, '2d')
        final_image_path = os.path.join(image_dir, "Product 2d Image.png") # Standardized name for final image
        
        # It's important to update current_image_path to the final image's path
        # if further operations (like model creation) depend on it.
        # However, for undo purposes, this finalized image is treated differently.
        with open(final_image_path, 'wb') as f:
            f.write(image_bytes)
        
        # current_image_path = final_image_path # Optional: update if needed post-finalization

        return jsonify({
            "success": True,
            "message": "Image finalized successfully",
            "image_path": f"/get-image/Product 2d Image.png" # Send specific filename
        })
    
    except Exception as e:
        print(f"Error finalizing image: {e}")
        return jsonify({
            "success": False,
            "message": f"Error finalizing image: {str(e)}"
        }), 500

@app.route('/get-image/<filename>')
def get_image(filename):
    global session_save_path 
    if not session_save_path:
        app.logger.error("session_save_path not set in get_image")
        return "Session not found", 404
    
    # Sanitize filename to prevent directory traversal
    filename = os.path.basename(filename)
    
    image_path = os.path.join(session_save_path, '2d', filename) 
    
    if os.path.exists(image_path):
        return send_file(image_path)
    else:
        # Fallback for non-session specific static images if any (though not used by create/edit image)
        # static_path = os.path.join('static', 'uploads', filename) # This was original
        # if os.path.exists(static_path):
        #      return send_file(static_path)
        app.logger.error(f"Image not found at {image_path}")
        return "Image not found", 404

@app.route('/undo-image-edit', methods=['POST'])
def undo_image_edit():
    global session_save_path, current_image_path
    
    if not session_save_path:
        return jsonify({"success": False, "message": "Session not found. Cannot undo."}), 400

    image_dir = os.path.join(session_save_path, '2d')
    if not os.path.isdir(image_dir):
        return jsonify({"success": False, "message": "Image directory not found. Cannot undo."}), 400

    # Get all .png images, excluding the finalized one
    try:
        image_files = [
            f for f in os.listdir(image_dir) 
            if f.endswith('.png') and f != "Product 2d Image.png"
        ]
    except FileNotFoundError:
         return jsonify({"success": False, "message": "Image directory not found."}), 400


    if not image_files:
        return jsonify({"success": False, "message": "No images found to undo."}), 400

    # Sort images by name (which includes timestamp) to get chronological order
    image_files.sort()

    if len(image_files) < 1: # Should be caught by "not image_files" but good for clarity
        # This case implies no images or only the final image exists (which is excluded)
        return jsonify({"success": False, "message": "No previous image version to revert to."}), 400
    
    if len(image_files) == 1:
        # Only one (non-finalized) image exists. We can delete it, but there's no "previous" to show.
        # The user request was: "delete the latest image" and "display the previous image".
        # This implies an undo operation should result in a previous image being shown.
        # So, if only one image is left (that can be undone), we cannot fulfill the "show previous" part.
        image_to_delete_path = os.path.join(image_dir, image_files[0])
        try:
            os.remove(image_to_delete_path)
            current_image_path = None # No current image after deleting the only one
            return jsonify({
                "success": True, 
                "message": "Last image removed. No further images to display.",
                "image_path": None # Signal to frontend to clear image
            })
        except OSError as e:
            app.logger.error(f"Error deleting image {image_to_delete_path}: {e}")
            return jsonify({"success": False, "message": f"Error deleting image: {str(e)}"}), 500

    # More than one image exists, proceed with undo
    image_to_delete_filename = image_files[-1]
    image_to_delete_path = os.path.join(image_dir, image_to_delete_filename)
    
    previous_image_filename = image_files[-2]
    previous_image_full_path = os.path.join(image_dir, previous_image_filename)

    try:
        os.remove(image_to_delete_path)
        current_image_path = previous_image_full_path # Update current_image_path
        return jsonify({
            "success": True,
            "image_path": f"/get-image/{previous_image_filename}",
            "message": "Reverted to the previous image."
        })
    except OSError as e:
        app.logger.error(f"Error deleting image {image_to_delete_path}: {e}")
        return jsonify({"success": False, "message": f"Error deleting image: {str(e)}"}), 500

@app.route('/get-image-history-status', methods=['GET'])
def get_image_history_status():
    global session_save_path
    if not session_save_path:
        return jsonify({"can_undo": False, "image_count": 0})

    image_dir = os.path.join(session_save_path, '2d')
    if not os.path.isdir(image_dir):
        return jsonify({"can_undo": False, "image_count": 0})

    try:
        # Count non-finalized images
        images = [
            f for f in os.listdir(image_dir) 
            if f.endswith('.png') and f != "Product 2d Image.png"
        ]
    except FileNotFoundError:
        return jsonify({"can_undo": False, "image_count": 0})
        
    image_count = len(images)
    # Can undo if there's more than one image that can be "undone".
    # If there is 1 image, deleting it means no image to revert to.
    # The request: "delete the latest image", "display the previous image".
    # This means at least 2 images must be present for a "successful" undo that shows a previous state.
    can_undo = image_count >= 1 
    # If image_count is 1, undo will delete it and result in no image.
    # If image_count is > 1, undo will delete the latest and show the one before it.
    # The frontend will decide based on the returned image_path from /undo-image-edit.
    # So, can_undo here means "is there at least one image that can be subject to an undo operation".
    return jsonify({"can_undo": can_undo, "image_count": image_count})

@app.route('/create-model', methods=['POST'])
def create_model():
    global session_save_path
    
    # Create 3d directory if it doesn't exist
    model_dir = os.path.join(session_save_path, '3d')
    os.makedirs(model_dir, exist_ok=True)
    
    try:
        # Get the path to the 2D image
        image_path = os.path.join(session_save_path, '2d', 'Product 2d Image.png')
        
        if not os.path.exists(image_path):
            return jsonify({
                "success": False,
                "message": "Product image not found"
            }), 400
        
        # Create the task in Meshy API and get the task ID
        task_id = meshy_api.create_image_to_3d_task(image_path)
        
        # Return the task ID for progress tracking
        return jsonify({
            "success": True,
            "message": "3D model creation started",
            "task_id": task_id
        })
    
    except Exception as e:
        print(f"Error creating 3D model task: {e}")
        return jsonify({
            "success": False,
            "message": f"Error creating 3D model task: {str(e)}"
        }), 500

@app.route('/download-model', methods=['POST'])
def download_model():
    global session_save_path
    
    data = request.json
    task_id = data.get('task_id')
    
    if not task_id:
        return jsonify({
            "success": False,
            "message": "No task ID provided"
        }), 400
    
    try:
        # Create 3d directory if it doesn't exist
        model_dir = os.path.join(session_save_path, '3d')
        os.makedirs(model_dir, exist_ok=True)
        
        # Get the task status
        task_status = meshy_api.retrieve_task_status(task_id)
        
        if task_status["status"] != "SUCCEEDED":
            return jsonify({
                "success": False,
                "message": f"Model is not ready. Current status: {task_status['status']}"
            }), 400
        
        # Download the model
        model_url = task_status["model_urls"]["glb"]
        final_model_path = os.path.join(model_dir, "Product 3D Model.glb")
        
        # Download the model file
        meshy_api.download_model(model_url, final_model_path)
        
        return jsonify({
            "success": True,
            "message": "3D model downloaded successfully",
            "model_path": f"/get-model/Product 3D Model.glb"
        })
    
    except Exception as e:
        print(f"Error downloading 3D model: {e}")
        return jsonify({
            "success": False,
            "message": f"Error downloading 3D model: {str(e)}"
        }), 500

@app.route('/get-model-progress', methods=['GET'])
def get_model_progress():
    # This route will be used to get the current progress of the model generation
    # It will be polled periodically by the frontend
    task_id = request.args.get('task_id')
    
    if not task_id:
        return jsonify({
            "success": False,
            "message": "No task ID provided"
        }), 400
    
    try:
        # Get the task status from Meshy API
        task_status = meshy_api.retrieve_task_status(task_id)
        status = task_status["status"]
        progress = task_status.get("progress", 0)
        
        return jsonify({
            "success": True,
            "status": status,
            "progress": progress
        })
    
    except Exception as e:
        print(f"Error getting model progress: {e}")
        return jsonify({
            "success": False,
            "message": f"Error getting model progress: {str(e)}"
        }), 500

@app.route('/view-model/<path:filename>')
def view_model(filename):
    # For paths coming from dashboard with project timestamp/path
    if '/' in filename:
        # Extract timestamp and model path
        parts = filename.split('/')
        timestamp = parts[0]
        model_filename = '/'.join(parts[1:])
        
        # Set model path
        model_dir = os.path.join("models", timestamp)
        model_path = os.path.join(model_dir, model_filename)
        
        if not os.path.exists(model_path):
            return "Model not found", 404
        
        # Render the glass model viewer template
        return render_template('glass_model_viewer.html', model_path=f"/get-model/{filename}")
    
    # For current session (backwards compatibility)
    else:
        if not session_save_path:
            return "No active session", 400
        
        model_path = os.path.join(session_save_path, '3d', filename)
        
        if not os.path.exists(model_path):
            return "Model not found", 404
        
        # Render the glass model viewer template
        return render_template('glass_model_viewer.html', model_path=f"/get-model/{filename}")

@app.route('/get-model/<path:filename>')
def get_model(filename):
    # For paths with timestamp/model format
    if '/' in filename:
        parts = filename.split('/')
        timestamp = parts[0]
        model_filename = '/'.join(parts[1:])
        
        model_path = os.path.join("models", timestamp, model_filename)
        
        if not os.path.exists(model_path):
            return "Model not found", 404
        
        return send_file(model_path, mimetype='model/gltf-binary')
    
    # For current session (backwards compatibility)
    else:
        if not session_save_path:
            return "No active session", 400
        
        model_path = os.path.join(session_save_path, '3d', filename)
        
        if not os.path.exists(model_path):
            return "Model not found", 404
        
        return send_file(model_path, mimetype='model/gltf-binary')

@app.route('/rename-project', methods=['POST'])
def rename_project():
    """API endpoint to rename a project"""
    data = request.json
    project_id = data.get('project_id')
    new_name = data.get('new_name')
    
    if not project_id or not new_name:
        return jsonify({"success": False, "message": "Missing project_id or new_name"}), 400
    
    try:
        # This endpoint is optional since we're using localStorage, 
        # but it's good to have for potential future server-side storage
        return jsonify({
            "success": True,
            "message": f"Project {project_id} renamed to {new_name}"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error renaming project: {str(e)}"
        }), 500

if __name__ == '__main__':
    # Create directories if they don't exist (Keep static/templates for Flask)
    os.makedirs("static", exist_ok=True) 
    os.makedirs("templates", exist_ok=True)
    # Ensure models directory exists (optional, as it's created per session)
    os.makedirs("models", exist_ok=True) 
    
    # Create default prompts if not exists
    # This assumes prompts are still stored relative to gpt_4_api.py
    if not os.path.exists("prompts"):
         gpt_4_api.create_default_prompts()
    
    app.run(debug=True, port=8080) 