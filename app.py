import streamlit as st
from pypdf import PdfReader
import genanki
import os
import random
import hashlib

st.set_page_config(page_title="Anki Card Generator", page_icon="🧠")

st.title("🧠 Anki Card Generator")
st.markdown("Upload a PDF and generate Anki cards based on your prompt")

uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

prompt = st.text_area(
    "Enter prompt for card generation",
    placeholder="e.g., Create flashcards for key concepts and definitions",
    height=100,
)

num_cards = st.slider(
    "Number of cards to generate", min_value=5, max_value=20, value=10
)

api_key = st.text_input(
    "OpenAI API Key (optional)", type="password", help="Leave empty to use sample cards"
)


def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text


def generate_sample_cards(text, num, user_prompt):
    """Generate sample cards from text - replace with AI in production"""
    words = text.split()
    key_terms = []

    for i, word in enumerate(words):
        if len(word) > 5 and random.random() < 0.01:
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
            "This refers to important information about {term}.",
        ),
        (
            "Fill blank",
            "{term} is important because:",
            "It appears frequently in the content.",
        ),
    ]

    cards = []
    for i, term in enumerate(key_terms):
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
        note = genanki.Note(model=model, fields=[card["front"], card["back"]])
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

            with st.spinner("Generating cards..."):
                if api_key:
                    st.info("API key provided - AI generation would happen here")
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
        with st.expander(f"Card {i}: {card['type']}"):
            st.markdown(f"**Front:** {card['front']}")
            st.markdown(f"**Back:** {card['back']}")

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
