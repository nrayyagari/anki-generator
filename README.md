# Anki Card Generator 🧠

Generate Anki decks from PDF documents. Upload a PDF, enter a prompt, and download an Anki deck (.apkg) to import into Anki.

## Features

- PDF upload and text extraction
- Custom prompt for card generation
- Adjustable number of cards
- Preview generated cards
- Download .apkg file for Anki

## Local Setup

```bash
# Clone and enter directory
git clone https://github.com/nrayyagari/anki-generator.git
cd anki-generator

# Create virtual environment
uv venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
uv pip install streamlit pypdf genanki python-dotenv

# Run the app
streamlit run app.py
```

The app will open at http://localhost:8501

## Usage

1. Upload a PDF file
2. Enter a prompt (e.g., "Create flashcards for key definitions")
3. Adjust number of cards with slider
4. Click "Generate Cards"
5. Preview cards and download .apkg file
6. Import the .apkg file into Anki

## API Integration (Optional)

To use AI-powered card generation, provide your OpenAI API key in the app. Without an API key, the app generates sample cards from the extracted text.

## Tech Stack

- **Streamlit** - UI framework
- **pypdf** - PDF text extraction
- **genanki** - Anki deck generation