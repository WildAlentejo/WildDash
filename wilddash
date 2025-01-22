import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time
from PIL import Image
from io import BytesIO
import os

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
camera_url = st.sidebar.text_input("Enter Camera JPG URL", "https://www.meteoalentejo.pt/cumulus/mertola/cam.jpg")

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
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Temperature", f"{current_weather['main']['temp']}°C")
    with col2:
        st.metric("Max Temperature", f"{current_weather['main']['temp_max']}°C")
    with col3:
        st.metric("Min Temperature", f"{current_weather['main']['temp_min']}°C")
    with col4:
        st.metric("Humidity", f"{current_weather['main']['humidity']}%")

    # Display weather icon
    weather_icon = current_weather['weather'][0]['icon']
    st.image(f"http://openweathermap.org/img/wn/{weather_icon}@2x.png", width=100)

# Display Weather Forecast (Compact and Stylish)
st.header("📅 Weather Forecast")
if forecast_weather:
    forecast_data = []
    for forecast in forecast_weather['list'][:5]:  # Show next 5 forecasts
        date_time = forecast['dt_txt']
        temp = forecast['main']['temp']
        weather_desc = forecast['weather'][0]['description']
        weather_icon = forecast['weather'][0]['icon']
        forecast_data.append([date_time, temp, weather_desc, weather_icon])
    
    # Display forecast in a compact and stylish way
    for forecast in forecast_data:
        with st.container():
            col1, col2, col3 = st.columns([1, 2, 1])
            with col1:
                st.image(f"http://openweathermap.org/img/wn/{forecast[3]}@2x.png", width=50)
            with col2:
                st.write(f"**{forecast[0]}**")
                st.write(f"{forecast[2]}")
            with col3:
                st.write(f"**{forecast[1]}°C**")
            st.markdown("---")  # Add a horizontal line for separation

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
