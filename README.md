# Product Design Assistant

A Flask-based web application that helps users design products through a structured 3-phase approach:

1. **Appearance Design Phase**: Create the visual and physical aspects of your product
2. **Commercial Application Phase**: Define market positioning and commercial strategy 
3. **Product Introduction Phase**: Get a unified product introduction document

The application features a modern glassmorphism UI with a chat interface for user interaction and dynamic content display.

## Features

- Interactive chat interface with OpenAI GPT models
- Real-time display of design summaries
- Markdown rendering for rich content presentation
- Elegant fade transitions between phases
- Responsive design for different screen sizes
- Glassmorphism UI styling

## Setup

### Prerequisites

- Python 3.8 or higher
- OpenAI API key

### Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## Usage

1. Start the Flask server:
   ```
   python app.py
   ```

2. Open a web browser and navigate to:
   ```
   http://127.0.0.1:5000/
   ```

3. Enter your name (optional) and start describing your product concept.

4. Follow the guided process:
   - Describe your product's appearance until satisfied, then type "Appearance design completed"
   - Define commercial aspects until satisfied, then type "Commercial application design finished."
   - View the final product introduction that combines both aspects

5. All generated documents are saved in the following directories:
   - `conversations/`: Chat history
   - `summary/`: Design summaries
   - `introduction/`: Final product introductions

## Technologies Used

- Backend: Flask, Python, OpenAI API
- Frontend: HTML, CSS, JavaScript
- Libraries: Marked.js (Markdown parsing), Prism.js (syntax highlighting)

## Project Structure

```
.
├── app.py                  # Main Flask application
├── gpt_4_api.py            # OpenAI API integration
├── prompts/                # Default prompt templates
├── static/                 # Static assets
│   ├── css/                # CSS stylesheets
│   └── js/                 # JavaScript files
├── templates/              # HTML templates
├── conversations/          # Generated conversation histories
├── summary/                # Generated design summaries
└── introduction/           # Generated product introductions
``` 