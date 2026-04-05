import streamlit as st
from pypdf import PdfReader
import genanki
import os
import random
import subprocess
import json

st.set_page_config(page_title="Anki Card Generator", page_icon="🧠")

st.title("🧠 Anki Card Generator")
st.markdown("Upload a PDF and generate Anki cards using your opencode CLI")

uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

prompt = st.text_area(
    "Enter prompt for card generation",
    placeholder="e.g., Create flashcards for key concepts and definitions",
    height=100,
)

num_cards = st.slider(
    "Number of cards to generate", min_value=5, max_value=20, value=10
)

use_opencode = st.checkbox("Use opencode CLI for smart card generation", value=True)


def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text


def generate_cards_with_opencode(text, num, user_prompt):
    """Generate cards using opencode CLI"""

    system_prompt = f"""You are an expert at creating Anki flashcards. 

Given the following text from a PDF, create {num} high-quality Anki cards based on this prompt: "{user_prompt}"

Generate EXACTLY {num} cards in the following JSON format:
[
  {{"front": "question 1", "back": "answer 1", "type": "type"}},
  {{"front": "question 2", "back": "answer 2", "type": "type"}}
]

Types should be one of: Definition, Question, Fill blank, Concept, Example

Return ONLY valid JSON array, no other text. Make questions clear and answers concise but informative.
"""

    truncated_text = text[:8000] if len(text) > 8000 else text

    full_prompt = f"{system_prompt}\n\nPDF Content:\n{truncated_text}"

    try:
        result = subprocess.run(
            ["opencode", "run", "--print-logs", "--format", "json", full_prompt],
            capture_output=True,
            text=True,
            timeout=120,
            env={**os.environ, "OPENCODE_MODEL": "opencode/minimax-m2.5-free"},
        )

        output = result.stdout + result.stderr

        json_match = None
        for line in output.split("\n"):
            if line.strip().startswith("[") or line.strip().startswith("{"):
                try:
                    json_match = json.loads(line)
                    break
                except:
                    continue

        if json_match and isinstance(json_match, list):
            return json_match[:num]

        lines = output.split("\n")
        for i, line in enumerate(lines):
            if "[" in line or "{" in line:
                try:
                    potential = "".join(lines[i:])
                    for j in range(len(potential), 0, -1):
                        try:
                            parsed = json.loads(potential[:j])
                            if isinstance(parsed, list):
                                return parsed[:num]
                        except:
                            continue
                except:
                    continue

        st.warning("Could not parse opencode response, using fallback")
        return None

    except Exception as e:
        st.error(f"Error using opencode: {e}")
        return None


def generate_sample_cards(text, num, user_prompt):
    """Generate sample cards from text - fallback"""
    words = text.split()
    key_terms = []

    for i, word in enumerate(words):
        if len(word) > 5 and random.random() < 0.005:
            key_terms.append(word.strip(".,!?;:"))

    key_terms = list(set(key_terms))[:num]

    card_types = [
        (
            "Definition",
            "What is {term}?",
            " {term} is a key concept from the document.",
        ),
        (
            "Question",
            "Can you explain {term}?",
            " This refers to important information about {term}.",
        ),
        (
            "Fill blank",
            "{term} is important because:",
            " It appears frequently in the content.",
        ),
    ]

    cards = []
    for term in key_terms:
        q_type, q, a = random.choice(card_types)
        cards.append(
            {
                "front": q.format(term=term[:20]),
                "back": a.format(term=term[:20]),
                "type": q_type,
            }
        )

    return cards


def create_anki_deck(cards, deck_name="PDF Notes"):
    model = genanki.Model(
        1607392320,
        "Basic Card",
        fields=[
            {"name": "Front"},
            {"name": "Back"},
        ],
        templates=[
            {
                "name": "Card 1",
                "qfmt": "{{Front}}",
                "afmt": "{{Front}}<hr id='answer'>{{Back}}",
            },
        ],
    )

    deck = genanki.Deck(random.randrange(1 << 30, 1 << 31), deck_name)

    for card in cards:
        note = genanki.Note(
            model=model, fields=[card.get("front", ""), card.get("back", "")]
        )
        deck.add_note(note)

    return deck


if st.button("Generate Cards", type="primary"):
    if uploaded_file is None:
        st.error("Please upload a PDF first")
    elif not prompt.strip():
        st.error("Please enter a prompt")
    else:
        with st.spinner("Reading PDF..."):
            text = extract_text_from_pdf(uploaded_file)

        if not text.strip():
            st.error("Could not extract text from PDF")
        else:
            st.success(f"PDF loaded: {len(text)} characters extracted")

            with st.spinner("Generating cards with opencode..."):
                if use_opencode:
                    cards = generate_cards_with_opencode(text, num_cards, prompt)
                    if not cards:
                        cards = generate_sample_cards(text, num_cards, prompt)
                else:
                    cards = generate_sample_cards(text, num_cards, prompt)

            st.session_state["cards"] = cards
            st.session_state["pdf_name"] = uploaded_file.name

if "cards" in st.session_state:
    cards = st.session_state["cards"]
    pdf_name = st.session_state.get("pdf_name", "notes")

    st.markdown("### 📇 Generated Cards")

    for i, card in enumerate(cards, 1):
        card_type = card.get("type", "Card")
        with st.expander(f"Card {i}: {card_type}"):
            st.markdown(f"**Front:** {card.get('front', '')}")
            st.markdown(f"**Back:** {card.get('back', '')}")

    st.markdown("---")
    st.markdown("### 📥 Download Anki Deck")

    deck_name = os.path.splitext(pdf_name)[0] or "PDF Notes"
    deck = create_anki_deck(cards, deck_name)

    output_file = f"{deck_name.replace(' ', '_')}.apkg"
    genanki.write_package(deck, output_file)

    with open(output_file, "rb") as f:
        st.download_button(
            label="⬇️ Download .apkg file",
            data=f,
            file_name=output_file,
            mime="application/apkg",
        )

    st.success(f"Deck '{deck_name}' created with {len(cards)} cards!")

st.markdown("---")
st.markdown("**Example prompts:**")
st.code("""
• Create flashcards for key definitions
• Generate questions and answers for each chapter
• Make cards for important dates and events
• Create fill-in-the-blank cards for terminology
""")
