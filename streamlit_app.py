import streamlit as st
from ghostfolio import Ghostfolio
import json

api_token = st.secrets["api"]["token"]


client = Ghostfolio(token=api_token)


st.title("🎈 My new app")
# st.write(
#     "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
# )

try:
    portfolio_details = json.dumps( client.details(), indent=4, ensure_ascii=False)
    print("Portfolio-Details:")
    print(portfolio_details)
    st.write(portfolio_details)
except Exception as e:
    print("Fehler beim Abrufen der Portfolio-Details:", e)

