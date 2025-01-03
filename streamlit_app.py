import streamlit as st
import requests
import pandas as pd

# Function to fetch live odds from the Odds API
def fetch_odds(api_url, api_key):
    response = requests.get(f"{api_url}&apiKey={api_key}")
    if response.status_code == 200:
        data = response.json()
        games = []
        for event in data:
            if "bookmakers" in event and event["bookmakers"]:
                bookmaker = event["bookmakers"][0]
                market = bookmaker.get("markets", [{}])[0]
                outcomes = market.get("outcomes", [])
                if len(outcomes) >= 2:
                    games.append({
                        "Sport": event.get("sport_key"),
                        "Home Team": event.get("home_team"),
                        "Away Team": event.get("away_team"),
                        "Commence Time": event.get("commence_time"),
                        "Bookmaker": bookmaker.get("title"),
                        "Home Odds": outcomes[0].get("price"),
                        "Away Odds": outcomes[1].get("price"),
                    })
        return pd.DataFrame(games)
    else:
        st.error(f"Failed to fetch data: {response.status_code}")
        return pd.DataFrame()

# Streamlit app interface
st.title("Betting Analysis Tool")
st.write("Fetch live odds, process them, and display recommendations.")

# Input fields for the Odds API
api_url = st.text_input("Enter Odds API URL", value="https://api.the-odds-api.com/v4/sports/upcoming/odds/?regions=us&markets=h2h&oddsFormat=american")
api_key = st.text_input("Enter Odds API Key", type="password")

# Fetch odds and display results
if st.button("Fetch Odds"):
    if api_url and api_key:
        odds_data = fetch_odds(api_url, api_key)
        if not odds_data.empty:
            st.write("### Live Odds Data")
            st.dataframe(odds_data)
        else:
            st.write("No data available.")
    else:
        st.error("Please enter both API URL and API Key.")
