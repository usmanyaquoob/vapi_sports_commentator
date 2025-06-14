import streamlit as st
import requests

def save_preferences(phone_number, sport, commentary_style, favorite_team, favorite_player):
    preferences = {
        "preferred_sport": sport,
        "commentary_style": commentary_style,
        "favorite_team": favorite_team,
        "favorite_player": favorite_player
    }
    payload = {
        "phone_number": phone_number,
        "preferences": preferences
    }
    response = requests.post("http://localhost:8000/save-preferences", json=payload)
    if response.status_code == 200:
        st.success("Preferences saved successfully!")
    else:
        st.error("Failed to save preferences.")

# Streamlit UI
st.title("Set Your Commentary Preferences")

phone_number = st.text_input("Phone Number")
sport = st.selectbox("Preferred Sport", ["football", "cricket"])
commentary_style = st.text_input("Commentary Style (e.g., snarky, neutral, enthusiastic)")
favorite_team = st.text_input("Favorite Team")
favorite_player = st.text_input("Favorite Player")

if st.button("Save Preferences"):
    if phone_number and sport and commentary_style and favorite_team and favorite_player:
        save_preferences(phone_number, sport, commentary_style, favorite_team, favorite_player)
    else:
        st.error("Please fill in all fields.")