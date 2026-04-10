from flask import Flask, request
from flask_socketio import SocketIO, join_room, leave_room, emit
import uuid
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# ==========================================
# FRONTEND: HTML/CSS/JS (Served from string)
# ==========================================
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Chat v0.4.0</title>
    <script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
    <style>
        body { font-family: system-ui, sans-serif; max-width: 600px; margin: 40px auto; padding: 20px; }
        #chatbox { height: 300px; border: 1px solid #ccc; overflow-y: auto; margin-bottom: 5px; padding: 10px; background: #fafafa;}
        .message { margin-bottom: 8px; padding: 5px; border-radius: 4px; }
        .system { color: #666; font-size: 0.9em; font-style: italic; }
        .me { color: #0d6efd; font-weight: bold;}
        .stranger { color: #dc3545; font-weight: bold;}
        .controls { display: flex; gap: 10px; margin-bottom: 10px; }
        input[type="text"] { flex-grow: 1; padding: 8px; }
        #typingIndicator { height: 20px; font-size: 0.8em; color: #888; font-style: italic; margin-bottom: 10px; }
    </style>
</head>
<body>
    <h2>Chat Prototype (v0.4.0)</h2>
    
    <div class="controls">
        <button id="startBtn">Start Search</button>
        <button id="skipBtn" disabled>Skip</button>
    </div>
    
    <div id="chatbox"></div>
    <div id="typingIndicator"></div>
    
    <div class="controls">
        <input type="text" id="messageInput" placeholder="Type a message..." disabled>
        <button id="sendBtn" disabled>Send</button>
    </div>

    <script>
        const socket = io(); 
        const chatbox = document.getElementById("chatbox");
        const messageInput = document.getElementById("messageInput");
        const typingIndicator = document.getElementById("typingIndicator");
        let typingTimeout;

        function printMessage(text, senderType) {
            const div = document.createElement("div");
            div.className = "message " + senderType;
            div.textContent = text;
            chatbox.appendChild(div);
            chatbox.scrollTop = chatbox.scrollHeight;
        }

        function setUIState(inChat) {
            document.getElementById("startBtn").disabled = true;
            document.getElementById("skipBtn").disabled = !inChat;
            document.getElementById("messageInput").disabled = !inChat;
            document.getElementById("sendBtn").disabled = !inChat;
            if (!inChat) typingIndicator.innerText = "";
        }

        document.getElementById("startBtn").onclick = () => {
            chatbox.innerHTML = "";
            socket.emit('start_search');
            document.getElementById("startBtn").disabled = true;
        };

        document.getElementById("skipBtn").onclick = () => {
            chatbox.innerHTML = "";
            setUIState(false);
            socket.emit('skip');
        };

        function sendMessage() {
            if (messageInput.value) {
                const text = messageInput.value;
                socket.emit('chat_message', { text: text });
                printMessage("You: " + text, "me");
                messageInput.value = "";
                socket.emit('typing', { is_typing: false });
            }
        }

        document.getElementById("sendBtn").onclick = sendMessage;
        
        messageInput.addEventListener("input", () => {
            socket.emit('typing', { is_typing: true });
            clearTimeout(typingTimeout);
            typingTimeout = setTimeout(() => {
                socket.emit('typing', { is_typing: false });
            }, 1500);
        });

        messageInput.addEventListener("keypress", (e) => {
            if (e.key === "Enter") sendMessage();
        });

        socket.on('system_message', (data) => {
            printMessage("[System] " + data.msg, "system");
        });

        socket.on('match_found', (data) => {
            chatbox.innerHTML = "";
            printMessage(`[System] You are now chatting with a stranger from ${data.country}. Say hi!`, "system");
            setUIState(true);
        });

        socket.on('chat_message', (data) => {
            typingIndicator.innerText = ""; 
            printMessage("Stranger: " + data.text, "stranger");
        });

        socket.on('typing', (data) => {
            typingIndicator.innerText = data.is_typing ? "Stranger is typing..." : "";
        });

        socket.on('stranger_disconnected', () => {
            printMessage("[System] Stranger has disconnected.", "system");
            setUIState(false);
        });
    </script>
</body>
</html>
"""

# ==========================================
# HTTP ROUTES
# ==========================================
@app.route('/')
def index():
    return HTML_PAGE

# ==========================================
# WEBSOCKET STATE & LOGIC
# ==========================================
waiting_queue = []
user_data = {}  
user_rooms = {} 
user_last_message = {} 
RATE_LIMIT_SECONDS = 0.5 

@socketio.on('connect')
def handle_connect():
    session_id = request.sid
    country = request.headers.get("CF-IPCountry", "Local")
    user_data[session_id] = {"country": country}

@socketio.on('start_search')
def handle_search():
    session_id = request.sid
    global waiting_queue
    
    if session_id in user_rooms or session_id in waiting_queue:
        return

    if waiting_queue:
        partner_id = waiting_queue.pop(0)
        room_id = str(uuid.uuid4())
        
        user_rooms[session_id] = room_id
        user_rooms[partner_id] = room_id

        join_room(room_id)
        join_room(room_id, sid=partner_id, namespace='/')

        emit('match_found', {'country': user_data[partner_id]['country']}, to=session_id)
        emit('match_found', {'country': user_data[session_id]['country']}, to=partner_id)
    else:
        waiting_queue.append(session_id)
        emit('system_message', {'msg': 'Waiting for a stranger to connect...'})

@socketio.on('chat_message')
def handle_message(data):
    session_id = request.sid
    
    current_time = time.time()
    last_time = user_last_message.get(session_id, 0)
    
    if current_time - last_time < RATE_LIMIT_SECONDS:
        emit('system_message', {'msg': 'Please slow down! You are sending messages too fast.'}, to=session_id)
        return
        
    user_last_message[session_id] = current_time

    if session_id in user_rooms:
        room_id = user_rooms[session_id]
        emit('chat_message', {'text': data['text']}, to=room_id, include_self=False)

@socketio.on('typing')
def handle_typing(data):
    session_id = request.sid
    if session_id in user_rooms:
        room_id = user_rooms[session_id]
        emit('typing', {'is_typing': data['is_typing']}, to=room_id, include_self=False)

@socketio.on('skip')
def handle_skip():
    session_id = request.sid
    cleanup_user(session_id)
    handle_search()

@socketio.on('disconnect')
def handle_disconnect():
    session_id = request.sid
    cleanup_user(session_id)
    if session_id in user_data:
        del user_data[session_id]

def cleanup_user(session_id):
    global waiting_queue
    if session_id in waiting_queue:
        waiting_queue.remove(session_id)
        
    if session_id in user_last_message:
        del user_last_message[session_id]
        
    if session_id in user_rooms:
        room_id = user_rooms[session_id]
        partner_id = next((sid for sid, rid in user_rooms.items() if rid == room_id and sid != session_id), None)
        
        del user_rooms[session_id]
        leave_room(room_id, sid=session_id, namespace='/')
        
        if partner_id:
            del user_rooms[partner_id]
            leave_room(room_id, sid=partner_id, namespace='/')
            emit('stranger_disconnected', to=partner_id)

if __name__ == '__main__':
    socketio.run(app, port=8000, debug=True)