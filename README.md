# Product Design Assistant

An end-to-end, conversation-driven product-design studio powered by Generative AI. Start with a raw idea and walk away with a market-ready design package that includes appearance specifications, a commercial strategy, high-resolution 2-D renders, and an interactable 3-D model.

---

##  Core Features

• **Multi-phase conversational workflow**
  1. **Appearance Design (Phase 1)** – refine form-factor, colours, materials and ergonomics.
  2. **Commercial Application (Phase 2)** – position the product, define customers, pricing & Go-To-Market.
  3. **Product Introduction (Phase 3)** – automatically synthesised executive brief that merges Phase 1 & 2.
  4. **2-D Image Generation (Phase 4)** – create, iterate and upscale a hero render of the product.
  5. **3-D Model Generation (Phase 5)** – generate a textured *.glb* model and preview it in-browser.

• **Unified glass-morphism UI** with chat, live markdown panels and smooth phase transitions.

• **Streaming status indicators** for long-running image & model generation jobs.

• **Automatic artefact management** – every session is saved under `models/<timestamp>/` with
  separate folders for conversation logs (**1d**), images (**2d**) and models (**3d**).

---

##  Tech Stack

| Backend | Frontend               | AI / External APIs                     |
| :------ | :--------------------- | :------------------------------------- |
| Flask   | Vanilla JS, HTML & CSS | OpenAI GPT-4o & DALL·E-3 "gpt-image-1" |
| Python  | Marked.js (Markdown)   | Google Gemini 2 Flash (image editing)  |
| Pillow  | Prism.js (code hl)     | Meshy v5 (2-D ➜ 3-D)                   |

---

##  Quick Start

### 1. Clone & set-up
```bash
$ git clone <repo-url>
$ cd product-design-assistant
$ python -m venv venv && source venv/bin/activate  # Windows: venv\Scripts\activate
$ pip install -r requirements.txt
```

### 2. Configure API keys
Create a `.env` file in the project root:
```env
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...
MESHY_API_KEY=...
```
(You may alternatively export the variables in your shell.)

### 3. Run the server
```bash
$ python app.py
# visit http://127.0.0.1:5000/ in your browser
```

---

## Usage Workflow

Inside the chat window, drive the conversation with the following keywords:

| Phase 1           | When finished type            |
| ----------------- | ----------------------------- |
| Appearance design | `Appearance design completed` |

| Phase 2                | When finished type                        |
| ---------------------- | ----------------------------------------- |
| Commercial application | `Commercial application design finished.` |

| Phase 3                  | Generate introduction |
| ------------------------ | --------------------- |
| `Generate Introduction.` |

| Phase 4             | Commands                |
| ------------------- | ----------------------- |
| Create first render | `create image`          |
| Iterate / edit      | *describe your change*  |
| Finalise & upscale  | `image design finished` |

| Phase 5            | Command        |
| ------------------ | -------------- |
| Generate 3-D model | `create model` |

All generated assets appear in the right-hand panel and are written to disk under `models/<timestamp>/`.

---

## Project Structure (simplified)
```text
.
├── app.py                 # Flask routes & phase logic
├── _1dto1d.py             # OpenAI helper & prompt engine
├── _2dto3d.py             # Meshy image➜3-D helper
├── prompts/               # Default prompt templates
├── templates/
│   └── index.html         # Main UI
├── static/
│   ├── css/style.css
│   └── js/script.js
└── models/                # Session output (auto-created)
    ├── 1d/ *.md           # Phase 1-3 markdown docs
    ├── 2d/ *.png          # Phase 4 images
    └── 3d/ *.glb          # Phase 5 models
```

---

## License

This project is released under the MIT License – see `LICENSE` for details.

---

## Contributing

Pull requests and issue reports are welcome! Please open an issue to discuss a new feature before
starting major work. 