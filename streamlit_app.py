import streamlit as st
import requests
import openai  # Optional
import os

# --- Konfiguration ---
GHOSTFOLIO_URL = st.secrets.get("GHOSTFOLIO_URL", "https://your-instance/api/v1")
GHOSTFOLIO_API_KEY = st.secrets.get("ghostfolio_token")
OPENAI_API_KEY = st.secrets.get("chatgpt_apikey", "")  # leer lassen wenn nicht genutzt

HEADERS = {
    "Authorization": f"Bearer {GHOSTFOLIO_API_KEY}",
    "Content-Type": "application/json"
}

# --- Funktionen ---
@st.cache_data(ttl=300)
def get_holdings():
    try:
        url = f"{GHOSTFOLIO_URL}/portfolio/details"
        res = requests.get(url, headers=HEADERS)
        res.raise_for_status()
        return res.json().get("holdings", {})
    except Exception as e:
        st.error(f"Fehler beim Abrufen der Holdings: {e}")
        return {}

def generate_response(symbol, data):
    if symbol not in data:
        return f"Keine Daten gefunden für Symbol: {symbol}"

    h = data[symbol]
    try:
        kaufpreis = h["investment"] / h["quantity"] if h["quantity"] else 0
        antwort = (
            f"Du hältst {h['quantity']} Anteile von {h['name']}.\n"
            f"- Kurs: {h['marketPrice']:.2f} €\n"
            f"- Kaufpreis: {kaufpreis:.2f} €\n"
            f"- Gesamtwert: {h['valueInBaseCurrency']:.2f} €\n"
            f"- Gewinn/Verlust: {h['netPerformance']:.2f} € "
            f"({h['netPerformancePercent'] * 100:.2f} %)"
        )
        return antwort
    except KeyError:
        return "Fehlende Daten für das Symbol."

def with_gpt(prompt):
    openai.api_key = OPENAI_API_KEY
    completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return completion.choices[0].message.content.strip()

# --- Streamlit UI ---
st.set_page_config(page_title="Ghostfolio Chat", layout="centered")
st.title("📈 Ghostfolio Chatbot")

query = st.chat_input("Frag etwas wie: Wie steht DTG.DE?")
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if query:
    with st.chat_message("user"):
        st.markdown(query)
    st.session_state.messages.append({"role": "user", "content": query})

    holdings = get_holdings()

    # Symbol extrahieren (sehr einfach)
    symbol = query.strip().split()[-1].replace("?", "").upper()

    antwort = generate_response(symbol, holdings)

    # Optional: GPT-Formulierung
    if OPENAI_API_KEY:
        antwort = with_gpt(f"Formuliere die folgende Portfolio-Antwort schön für den Nutzer: {antwort}")

    with st.chat_message("assistant"):
        st.markdown(antwort)
    st.session_state.messages.append({"role": "assistant", "content": antwort})