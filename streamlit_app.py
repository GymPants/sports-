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

# Function to calculate recommendations based on odds
def calculate_recommendations(data):
    recommendations = []
    for _, row in data.iterrows():
        # Example formula for success probability
        home_win_probability = 1 / abs(row['Home Odds']) if row['Home Odds'] else 0
        away_win_probability = 1 / abs(row['Away Odds']) if row['Away Odds'] else 0
        # Highlight close games and favorable odds
        if home_win_probability > away_win_probability:
            recommendations.append({
                "Game": f"{row['Home Team']} vs {row['Away Team']}",
                "Pick": f"{row['Home Team']} to win",
                "Confidence": round(home_win_probability * 100, 2),
                "Reasoning": "Favorable odds and higher implied probability for the home team."
            })
        else:
            recommendations.append({
                "Game": f"{row['Home Team']} vs {row['Away Team']}",
                "Pick": f"{row['Away Team']} to win",
                "Confidence": round(away_win_probability * 100, 2),
                "Reasoning": "Better implied probability for the away team."
            })
    return pd.DataFrame(recommendations)

# Streamlit app interface
st.title("Betting Analysis Tool")
st.write("Fetch live odds, analyze them, and get recommendations.")

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
            
            # Calculate recommendations
            st.write("### Betting Recommendations")
            recommendations = calculate_recommendations(odds_data)
            st.dataframe(recommendations)
        else:
            st.write("No data available.")
    else:
        st.error("Please enter both API URL and API Key.")

