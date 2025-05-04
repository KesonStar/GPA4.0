from flask import Flask, render_template, request, jsonify
import gpt_4_api
import os
import datetime  # Add datetime import
from dotenv import load_dotenv

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

@app.route('/')
def index():
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
            product_introduction = gpt_4_api.generate_product_introduction(appearance_summary, commercial_summary)
            
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
    
    # Phase 3: Already completed
    else:
        return jsonify({
            "response": "The product design process has been completed. Refresh the page to start a new design.",
            "phase": current_phase
        })

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
    
    app.run(debug=True) 