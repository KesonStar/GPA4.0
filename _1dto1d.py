from openai import OpenAI
import os
import time
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure OpenAI API key
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "your_api_key_here")
client = OpenAI(api_key=OPENAI_API_KEY)

def load_prompt(prompt_name):
    """Load prompt from file in the prompts directory"""
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct path to prompts directory
    prompts_dir = os.path.join(script_dir, "prompts")
    # Ensure prompts directory exists
    os.makedirs(prompts_dir, exist_ok=True)
    
    # Construct path to prompt file
    prompt_path = os.path.join(prompts_dir, f"{prompt_name}.txt")
    
    # Check if file exists
    if not os.path.exists(prompt_path):
        # Create default prompt if file doesn't exist
        default_prompts = {
            "appearance_conversation": """You are a product appearance design expert, helping users refine the visual and physical aspects of their product.
            
Your goals are:
1. Understand the user's product purpose and intended use cases
2. Help users clarify key visual and physical design elements including:
   - Form factor and dimensions
   - Materials and textures
   - Color schemes and aesthetic style
   - User interface elements (if applicable)
   - Ergonomics and physical interaction points
3. Guide users to consider how appearance supports functionality
4. Ask targeted questions to refine appearance details

Please maintain a friendly, professional attitude and focus exclusively on appearance design aspects.
Remind the user they can type "Appearance design completed" when they are satisfied with the appearance design.
Do not move to business considerations or implementation details.""",
            
            "commercial_conversation": """You are a product commercialization expert, helping users refine the business and market aspects of their product.
            
Your goals are:
1. Understand the product's market positioning and target audience
2. Help users clarify key commercial elements including:
   - Target market segments and customer profiles
   - Pricing strategy and business model
   - Distribution channels and go-to-market strategy
   - Competitive advantages and unique selling propositions
   - Marketing and branding approach
3. Guide users to consider commercial viability and market fit
4. Ask targeted questions to refine commercial details

Please maintain a friendly, professional attitude and focus exclusively on commercial application aspects.
Remind the user they can type "Commercial application design finished." when they are satisfied with the commercial design.
Build upon the product's appearance design that was already completed in the previous phase.""",
            
            "appearance_summary": """You are a product appearance design document specialist. Your task is to analyze the provided conversation 
between a user and an AI assistant about product appearance design, and create a comprehensive, well-structured 
product appearance design document.

Your output should:
1. Extract and organize all key product appearance information
2. Include detailed sections on:
   - Overall product form factor and dimensions
   - Materials, textures, and finishes
   - Color schemes and aesthetic style
   - User interface visual elements (if applicable)
   - Ergonomics and physical interaction points
3. Be formatted in clean, professional markdown with appropriate headings, lists, and emphasis
4. Include a clear product definition section at the beginning
5. Focus ONLY on appearance design aspects, not business value or implementation details

Create a standalone document that a design team could use to visualize and create the product's appearance.""",
            
            "commercial_summary": """You are a product commercialization document specialist. Your task is to analyze the provided conversation 
between a user and an AI assistant about product commercial applications, and create a comprehensive, well-structured 
product commercialization document.

Your output should:
1. Extract and organize all key product commercialization information
2. Include detailed sections on:
   - Target market segments and customer profiles
   - Pricing strategy and business model
   - Distribution channels and go-to-market strategy
   - Competitive advantages and unique selling propositions
   - Marketing and branding approach
3. Be formatted in clean, professional markdown with appropriate headings, lists, and emphasis
4. Focus ONLY on commercial application aspects

Create a standalone document that a business team could use to commercialize the product.""",
            
            "product_introduction": """You are a product introduction specialist. Your task is to synthesize information from both 
the product appearance design document and the commercial application document to create a comprehensive, 
compelling product introduction.

Your output should:
1. Begin with an executive summary that captures the essence of the product
2. Include detailed sections that integrate both appearance and commercial aspects:
   - Product Overview (combining physical design with market positioning)
   - Key Features and Benefits (linking appearance elements to commercial advantages)
   - Target Market and Use Cases
   - Design Philosophy and Aesthetics
   - Commercial Strategy Highlights
3. Be formatted in clean, professional markdown with appropriate headings, lists, and emphasis
4. Create a cohesive narrative that flows naturally between design and commercial aspects
5. Use language appropriate for stakeholders, investors, or marketing materials

Create a polished, comprehensive product introduction that could be used for presentations, pitches, or marketing materials."""
        }
        
        # Write default prompt to file
        with open(prompt_path, "w", encoding="utf-8") as f:
            f.write(default_prompts.get(prompt_name, "Default prompt content"))
    
    # Read prompt from file
    with open(prompt_path, "r", encoding="utf-8") as f:
        prompt_content = f.read()
    
    return prompt_content

def initialize_appearance_conversation():
    """Initialize conversation with system prompt for the appearance design phase (LLM1)"""
    return [
        {
            "role": "system", 
            "content": load_prompt("appearance_conversation")
        }
    ]

def initialize_commercial_conversation():
    """Initialize conversation with system prompt for the commercial application phase (LLM3)"""
    return [
        {
            "role": "system", 
            "content": load_prompt("commercial_conversation")
        }
    ]

def initialize_appearance_summary_system():
    """Initialize system prompt for the appearance summary GPT (LLM2)"""
    return {
        "role": "system", 
        "content": load_prompt("appearance_summary")
    }

def initialize_commercial_summary_system():
    """Initialize system prompt for the commercial summary GPT (LLM3)"""
    return {
        "role": "system", 
        "content": load_prompt("commercial_summary")
    }

def initialize_product_introduction_system():
    """Initialize system prompt for the final product introduction GPT (LLM4)"""
    return {
        "role": "system", 
        "content": load_prompt("product_introduction")
    }

def save_conversation_to_markdown(conversation, phase, base_save_path, user_name="User"):
    """Save conversation to markdown file within the session-specific path"""
    # Define the target directory
    target_dir = os.path.join(base_save_path, '1d')
    # Create directory if not exists
    os.makedirs(target_dir, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(target_dir, f"{phase}_design_{timestamp}.md")
    
    # Create markdown content
    markdown_content = f"# Product {phase.capitalize()} Design Conversation - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    # Add conversation content
    markdown_content += "## Conversation History\n\n"
    for message in conversation:
        if message["role"] == "system":
            continue  # Skip system messages
        elif message["role"] == "user":
            markdown_content += f"### {user_name}\n\n{message['content']}\n\n"
        elif message["role"] == "assistant":
            markdown_content += f"### AI Assistant\n\n{message['content']}\n\n"
    
    # Save file
    with open(filename, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    
    return filename

def save_summary_to_markdown(summary, phase, base_save_path):
    """Save summary to markdown file within the session-specific path"""
    # Define the target directory
    target_dir = os.path.join(base_save_path, '1d')
    # Create directory if not exists
    os.makedirs(target_dir, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(target_dir, f"{phase}_design_summary_{timestamp}.md")
    
    # Save file
    with open(filename, "w", encoding="utf-8") as f:
        f.write(summary)
    
    return filename

def save_introduction_to_markdown(introduction, base_save_path):
    """Save product introduction to markdown file within the session-specific path"""
    # Define the target directory
    target_dir = os.path.join(base_save_path, '1d')
    # Create directory if not exists
    os.makedirs(target_dir, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(target_dir, f"product_introduction_{timestamp}.md")
    
    # Save file
    with open(filename, "w", encoding="utf-8") as f:
        f.write(introduction)
    
    return filename

def chat_completion(messages, model="gpt-4.1-mini", temperature=0.7):
    """Call OpenAI API to get response with specified model"""
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"API call error: {e}")
        return "Sorry, I encountered an issue. Please try again later."

def generate_appearance_summary(conversation, user_name):
    """Generate product appearance design summary using LLM2"""
    # Create a new conversation for the summary GPT
    summary_messages = [initialize_appearance_summary_system()]
    
    # Add conversation context (excluding system messages)
    summary_messages.append({
        "role": "user", 
        "content": f"Below is a conversation between {user_name} and an AI assistant about product appearance design. Please analyze this conversation and create a comprehensive product appearance design document:\n\n"
    })
    
    # Format conversation for the summary GPT
    conversation_text = ""
    for message in conversation:
        if message["role"] == "system":
            continue  # Skip system messages
        elif message["role"] == "user":
            conversation_text += f"{user_name}: {message['content']}\n\n"
        elif message["role"] == "assistant":
            conversation_text += f"AI Assistant: {message['content']}\n\n"
    
    # Add formatted conversation to the summary request
    summary_messages.append({
        "role": "user",
        "content": conversation_text
    })
    
    # Add final instruction
    summary_messages.append({
        "role": "user",
        "content": "Based on the conversation above, please create a comprehensive product appearance design document in markdown format. Include a clear product definition section at the beginning and focus exclusively on appearance design aspects."
    })
    
    # Get summary from LLM2
    summary = chat_completion(
        summary_messages, 
        model="gpt-4-turbo",
        temperature=0.5  # Lower temperature for more focused output
    )
    
    return summary

def generate_commercial_summary(conversation, user_name):
    """Generate product commercial application summary using LLM3"""
    # Create a new conversation for the summary GPT
    summary_messages = [initialize_commercial_summary_system()]
    
    # Add conversation context (excluding system messages)
    summary_messages.append({
        "role": "user", 
        "content": f"Below is a conversation between {user_name} and an AI assistant about product commercial application design. Please analyze this conversation and create a comprehensive product commercialization document:\n\n"
    })
    
    # Format conversation for the summary GPT
    conversation_text = ""
    for message in conversation:
        if message["role"] == "system":
            continue  # Skip system messages
        elif message["role"] == "user":
            conversation_text += f"{user_name}: {message['content']}\n\n"
        elif message["role"] == "assistant":
            conversation_text += f"AI Assistant: {message['content']}\n\n"
    
    # Add formatted conversation to the summary request
    summary_messages.append({
        "role": "user",
        "content": conversation_text
    })
    
    # Add final instruction
    summary_messages.append({
        "role": "user",
        "content": "Based on the conversation above, please create a comprehensive product commercial application document in markdown format. Focus exclusively on commercial aspects."
    })
    
    # Get summary from LLM3
    summary = chat_completion(
        summary_messages, 
        model="gpt-4.1",
        temperature=0.5  # Lower temperature for more focused output
    )
    
    return summary

def generate_product_introduction(appearance_summary, commercial_summary, appearance_conversation):
    """Generate final product introduction using LLM4"""
    # Create a new conversation for the introduction GPT
    intro_messages = [initialize_product_introduction_system()]
    
    # Format appearance conversation for context
    appearance_conversation_text = ""
    for message in appearance_conversation:
        if message["role"] == "system":
            continue  # Skip system messages
        elif message["role"] == "user":
            appearance_conversation_text += f"User: {message['content']}\n\n"
        elif message["role"] == "assistant":
            appearance_conversation_text += f"AI Assistant: {message['content']}\n\n"
    
    # Add summaries and appearance conversation to the introduction request
    intro_messages.append({
        "role": "user", 
        "content": f"Below are two documents: 1) a product appearance design document and 2) a product commercial application document, as well as the original appearance design conversation. Please synthesize these into a comprehensive product introduction:\n\n"
                  f"## PRODUCT APPEARANCE DESIGN DOCUMENT\n\n{appearance_summary}\n\n"
                  f"## PRODUCT COMMERCIAL APPLICATION DOCUMENT\n\n{commercial_summary}\n\n"
                  f"## ORIGINAL APPEARANCE DESIGN CONVERSATION\n\n{appearance_conversation_text}\n\n"
                  f"Please create a polished, comprehensive product introduction that integrates both the appearance design and commercial aspects into a cohesive narrative."
    })
    
    # Get introduction from LLM4
    introduction = chat_completion(
        intro_messages, 
        model="gpt-4.1-mini",
        temperature=0.6  # Slightly higher temperature for creative synthesis
    )
    
    return introduction

def create_default_prompts():
    """Create default prompt files if they don't exist"""
    prompt_names = [
        "appearance_conversation",
        "commercial_conversation",
        "appearance_summary",
        "commercial_summary",
        "product_introduction"
    ]
    
    for prompt_name in prompt_names:
        load_prompt(prompt_name)  # This will create the file if it doesn't exist
    
    print("Default prompt files have been created in the 'prompts' directory.")
    print("You can modify these files to customize the behavior of the AI assistants.")

def main():
    # Check if this is the first run and create default prompt files
    create_default_prompts()

    user_name = input("Enter your name (for conversation logs): ")

    # Phase 1: Appearance Design
    print("\n--- Phase 1: Appearance Design ---")
    appearance_conversation = initialize_appearance_conversation()
    # Simulate conversation ...
    appearance_summary = generate_appearance_summary(appearance_conversation, user_name)
    
    # Example save paths for main function execution
    main_save_path = os.path.join("models", datetime.now().strftime("%Y%m%d_%H%M%S_main"))
    os.makedirs(main_save_path, exist_ok=True)
    
    # Save appearance conversation
    appearance_conversation_file = save_conversation_to_markdown(appearance_conversation, "appearance", main_save_path, user_name)
    print(f"\nAppearance design conversation saved to: {appearance_conversation_file}")
    
    # Save appearance summary
    appearance_summary_file = save_summary_to_markdown(appearance_summary, "appearance", main_save_path)
    print(f"\nAppearance design summary saved to: {appearance_summary_file}")

    # Phase 2: Commercial Application Design
    print("\n--- Phase 2: Commercial Application Design ---")
    commercial_conversation = initialize_commercial_conversation()
    commercial_conversation.append({
        "role": "user", 
        "content": f"Appearance design summary:\n{appearance_summary}\nNow let's discuss commercial aspects."
    })
    # Simulate conversation ...
    commercial_summary = generate_commercial_summary(commercial_conversation, user_name)
    
    # Save commercial conversation
    commercial_conversation_file = save_conversation_to_markdown(commercial_conversation, "commercial", main_save_path, user_name)
    print(f"\nCommercial design conversation saved to: {commercial_conversation_file}")
    
    # Save commercial summary
    commercial_summary_file = save_summary_to_markdown(commercial_summary, "commercial", main_save_path)
    print(f"\nCommercial design summary saved to: {commercial_summary_file}")

    # Phase 3: Product Introduction
    print("\n--- Phase 3: Product Introduction ---")
    product_introduction = generate_product_introduction(appearance_summary, commercial_summary, appearance_conversation)
    
    # Save product introduction
    introduction_file = save_introduction_to_markdown(product_introduction, main_save_path)
    print(f"\nProduct introduction saved to: {introduction_file}")

if __name__ == "__main__":
    main()
