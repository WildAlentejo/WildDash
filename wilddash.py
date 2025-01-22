import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time
from PIL import Image
from io import BytesIO
import os
import plotly.graph_objects as go  # For creating professional graphs

# OpenWeatherMap API Key (replace with your own)
API_KEY = "e3a6729ad886ce16e51118467f080ed8"
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "http://api.openweathermap.org/data/2.5/forecast"

# Streamlit App Title
st.set_page_config(page_title="Farm Dashboard", layout="wide")
st.title("🌾 Farm Dashboard")

# Sidebar for user inputs
st.sidebar.header("Settings")
location = st.sidebar.text_input("Enter Farm Location", "Montes Altos, PT")
camera_url = st.sidebar.text_input("Enter Camera JPG URL", "http://your-camera-ip/image.jpg")

# Function to fetch weather data
def get_weather(city):
    try:
        # Current weather
        current_params = {"q": city, "appid": API_KEY, "units": "metric"}
        current_response = requests.get(BASE_URL, params=current_params).json()
        
        # Weather forecast
        forecast_params = {"q": city, "appid": API_KEY, "units": "metric"}
        forecast_response = requests.get(FORECAST_URL, params=forecast_params).json()
        
        return current_response, forecast_response
    except Exception as e:
        st.error(f"Error fetching weather data: {e}")
        return None, None

# Display Current Weather
st.header("🌤️ Current Weather")
current_weather, forecast_weather = get_weather(location)

if current_weather:
    # Basic weather info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Temperature", f"{current_weather['main']['temp']}°C")
    with col2:
        st.metric("Humidity", f"{current_weather['main']['humidity']}%")
    with col3:
        st.metric("Wind Speed", f"{current_weather['wind']['speed']} m/s")

    # Additional weather info
    col4, col5, col6 = st.columns(3)
    with col4:
        st.metric("Pressure", f"{current_weather['main']['pressure']} hPa")
    with col5:
        visibility_km = current_weather.get('visibility', 0) / 1000  # Convert meters to kilometers
        st.metric("Visibility", f"{visibility_km:.1f} km")
    with col6:
        st.metric("Cloudiness", f"{current_weather['clouds']['all']}%")

    # Sunrise and Sunset
    sunrise_time = datetime.fromtimestamp(current_weather['sys']['sunrise']).strftime('%H:%M:%S')
    sunset_time = datetime.fromtimestamp(current_weather['sys']['sunset']).strftime('%H:%M:%S')
    col7, col8 = st.columns(2)
    with col7:
        st.metric("Sunrise", sunrise_time)
    with col8:
        st.metric("Sunset", sunset_time)

    # Rain and Snow (if available)
    if 'rain' in current_weather:
        rain_volume = current_weather['rain'].get('1h', 0)  # Rain volume in the last hour
        st.metric("Rain (Last Hour)", f"{rain_volume} mm")
    if 'snow' in current_weather:
        snow_volume = current_weather['snow'].get('1h', 0)  # Snow volume in the last hour
        st.metric("Snow (Last Hour)", f"{snow_volume} mm")

    # Display weather icon
    weather_icon = current_weather['weather'][0]['icon']
    st.image(f"http://openweathermap.org/img/wn/{weather_icon}@2x.png", width=100)

# Display Weather Forecast (Compact and Stylish)
st.header("📅 Weather Forecast")
if forecast_weather:
    # Group forecast data by day
    forecast_by_day = {}
    for forecast in forecast_weather['list']:
        date = forecast['dt_txt'].split()[0]  # Extract date (YYYY-MM-DD)
        if date not in forecast_by_day:
            forecast_by_day[date] = {
                "temps": [],
                "weather": [],
                "icons": []
            }
        forecast_by_day[date]["temps"].append(forecast['main']['temp'])
        forecast_by_day[date]["weather"].append(forecast['weather'][0]['description'])
        forecast_by_day[date]["icons"].append(forecast['weather'][0]['icon'])

    # Display forecast in a compact table
    st.write("**Daily Forecast**")
    for date, data in forecast_by_day.items():
        min_temp = min(data["temps"])
        max_temp = max(data["temps"])
        avg_weather = max(set(data["weather"]), key=data["weather"].count)  # Most frequent weather description
        avg_icon = max(set(data["icons"]), key=data["icons"].count)  # Most frequent weather icon

        col1, col2, col3, col4 = st.columns([1, 2, 1, 1])
        with col1:
            st.image(f"http://openweathermap.org/img/wn/{avg_icon}@2x.png", width=50)
        with col2:
            st.write(f"**{date}**")
            st.write(f"{avg_weather}")
        with col3:
            st.write(f"**Max:** {max_temp}°C")
        with col4:
            st.write(f"**Min:** {min_temp}°C")
        st.markdown("---")  # Add a horizontal line for separation

# Create a Plotly Graph for Weather Data
st.header("📊 Weather Trends")
if forecast_weather:
    # Extract data for the graph
    dates = []
    temps = []
    humidity = []
    rain_prob = []
    rain_mm = []

    for forecast in forecast_weather['list']:
        dates.append(forecast['dt_txt'])
        temps.append(forecast['main']['temp'])
        humidity.append(forecast['main']['humidity'])
        rain_prob.append(forecast.get('pop', 0) * 100)  # Probability of precipitation (0-100%)
        rain_mm.append(forecast.get('rain', {}).get('3h', 0))  # Rain volume in mm (last 3 hours)

    # Create a Plotly figure
    fig = go.Figure()

    # Add Temperature trace
    fig.add_trace(go.Scatter(
        x=dates, y=temps, mode='lines+markers', name='Temperature (°C)',
        line=dict(color='red', width=2), marker=dict(size=8)
    ))

    # Add Humidity trace
    fig.add_trace(go.Scatter(
        x=dates, y=humidity, mode='lines+markers', name='Humidity (%)',
        line=dict(color='blue', width=2), marker=dict(size=8)
    ))

    # Add Rain Probability trace
    fig.add_trace(go.Scatter(
        x=dates, y=rain_prob, mode='lines+markers', name='Rain Probability (%)',
        line=dict(color='green', width=2), marker=dict(size=8)
    ))

    # Add Rain Volume trace
    fig.add_trace(go.Scatter(
        x=dates, y=rain_mm, mode='lines+markers', name='Rain Volume (mm)',
        line=dict(color='purple', width=2), marker=dict(size=8)
    ))

    # Update layout for a professional look
    fig.update_layout(
        title="Weather Trends Over Time",
        xaxis_title="Date & Time",
        yaxis_title="Values",
        legend_title="Metrics",
        template="plotly_white",
        hovermode="x unified"
    )

    # Display the graph
    st.plotly_chart(fig, use_container_width=True)

# Calendar with Events
st.header("📅 Farm Calendar")

# Load saved events from file
try:
    with open("farm_events.txt", "r") as f:
        calendar_events = [line.strip().split("|") for line in f.readlines()]
except FileNotFoundError:
    calendar_events = []

# Add event to calendar
event_date = st.date_input("Select Date")
event_name = st.text_input("Event Name")
if st.button("Add Event"):
    calendar_events.append([str(event_date), event_name])  # Store as a list
    with open("farm_events.txt", "a") as f:
        f.write(f"{event_date}|{event_name}\n")
    st.success(f"Event '{event_name}' added on {event_date}")

# Display Calendar with Delete Option
if calendar_events:
    st.write("Upcoming Events:")
    for i, event in enumerate(calendar_events):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.write(f"- {event[1]} on {event[0]}")
        with col2:
            if st.button(f"Delete {i+1}"):
                # Remove the event from the list
                calendar_events.pop(i)
                # Rewrite the file without the deleted event
                with open("farm_events.txt", "w") as f:
                    for ev in calendar_events:
                        f.write(f"{ev[0]}|{ev[1]}\n")
                st.rerun()  # Refresh the app to reflect changes

# Notepad
st.header("📝 Notepad")
note = st.text_area("Write your notes here")
if st.button("Save Note"):
    with open("farm_notes.txt", "a") as f:
        f.write(f"{datetime.now()}: {note}\n")
    st.success("Note saved!")

# Display Saved Notes with Delete Option
st.header("📖 Saved Notes")
try:
    with open("farm_notes.txt", "r") as f:
        saved_notes = f.readlines()
    if saved_notes:
        for i, note in enumerate(saved_notes):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(note)
            with col2:
                if st.button(f"Delete {i+1}", key=f"note_{i}"):
                    # Remove the note from the list
                    saved_notes.pop(i)
                    # Rewrite the file without the deleted note
                    with open("farm_notes.txt", "w") as f:
                        for n in saved_notes:
                            f.write(n)
                    st.rerun()  # Refresh the app to reflect changes
    else:
        st.write("No notes saved yet.")
except FileNotFoundError:
    st.write("No notes saved yet.")

# Planting Calendar
st.header("🌱 Planting Calendar")
planting_data = {
    "Crop": ["Tomatoes", "Carrots", "Potatoes", "Lettuce"],
    "Planting Month": ["March", "April", "February", "May"],
    "Harvest Month": ["August", "July", "June", "September"]
}
planting_df = pd.DataFrame(planting_data)
st.dataframe(planting_df)

# Camera Feed (JPG URL)
st.header("📷 Camera Feed")
if camera_url:
    try:
        # Fetch the image from the URL
        response = requests.get(camera_url)
        if response.status_code == 200:
            # Convert the image to a format Streamlit can display
            image = Image.open(BytesIO(response.content))
            st.image(image, caption="Latest Camera Image", use_container_width=True)
        else:
            st.warning(f"Unable to fetch image. Status code: {response.status_code}")
    except Exception as e:
        st.error(f"Error fetching camera image: {e}")
else:
    st.warning("Please enter a valid camera JPG URL.")

# Notifications/Alarms
st.header("🔔 Notifications")
if st.button("Test Notification"):
    st.toast("This is a test notification!", icon="🔔")

# Automatically refresh the app every 100 seconds
if st.button("Refresh App"):
    st.rerun()

# Schedule automatic refresh every 100 seconds
time.sleep(100)
st.rerun()

# Run the app
if __name__ == "__main__":
    st.write("Welcome to your Farm Dashboard!")
