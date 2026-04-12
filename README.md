> **Disclaimer:** This project has been entirely developed and generated using Google Gemini.

# Elgemo 💬

![Version](https://img.shields.io/badge/version-1.0.6-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0.3-black.svg)
![Socket.IO](https://img.shields.io/badge/Socket.IO-5.3.6-black.svg)

Elgemo is a fast, modern, and anonymous real-time chat application. Built with Flask and WebSockets, it pairs users instantly while maintaining a clean, glassmorphic UI that works flawlessly across desktop and mobile devices.

## ✨ Features

* **Real-Time Messaging:** Powered by WebSockets (`Flask-SocketIO`) for zero-latency communication.
* **Smart Matchmaking:** Instantly pairs users in a waiting queue and handles graceful disconnects.
* **Advanced Mobile UI:** * Implements the `window.visualViewport` API for a definitive fix to virtual keyboard overlapping on iOS and Android.
  * Prevents iOS "elastic bounce" scrolling.
* **Safety First:** * Built-in profanity filter (`better-profanity`).
  * Automatic 5-minute IP bans for users who trigger the filter 3 times.
* **Dynamic Theming:** Light and Dark modes with user preference saved to `localStorage`.
* **Live Status Updates:** Real-time online user count and typing indicators.

## 🛠️ Tech Stack

**Backend:**
* Python 3.8+
* Flask
* Flask-SocketIO (WebSocket handling)
* better-profanity (Text sanitization)

**Frontend:**
* HTML5 / CSS3 (Custom Glassmorphism design)
* Vanilla JavaScript
* Socket.IO Client

## 🚀 Quick Start

### 1. Prerequisites
Ensure you have Python 3.8 or higher installed on your machine.

### 2. Installation

Clone the repository and navigate to the project directory:
git clone https://github.com/yourusername/elgemo.git
cd elgemo

Create and activate a virtual environment (recommended):
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate

Install the required dependencies:
pip install -r requirements.txt

### 3. Environment Variables
Create a `.env` file in the root directory to configure the application (optional but recommended for production):

SECRET_KEY=your-super-secret-key
PORT=8000
DEBUG=True

### 4. Run the Application
Start the server:
python app.py

Open your web browser and navigate to http://localhost:8000.

*(Note: The development server uses `allow_unsafe_werkzeug=True` for easy local testing. For production deployments, please use a production-ready WSGI/ASGI server like Gunicorn with Eventlet or Gevent).*

## 📱 The Mobile Keyboard Fix
Elgemo features a highly robust solution for mobile browser viewport issues. Instead of relying on buggy `100vh` or `100dvh` CSS rules, Elgemo binds its application height directly to the `window.visualViewport.height` JavaScript API. This dynamically recalculates the exact visible pixel space left over *after* the keyboard renders, ensuring the input bar is never hidden behind the system keyboard.

## 📜 License
Distributed under the MIT License. See `LICENSE` for more information.