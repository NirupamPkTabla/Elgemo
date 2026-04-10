from flask import Flask, request
from flask_socketio import SocketIO, join_room, leave_room, emit
import uuid
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# ==========================================
# FRONTEND: HTML/CSS/JS (Elgemo v0.7.3)
# ==========================================
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Elgemo</title>
    <script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
    <style>
        /* 1. Base Variables (Dark Mode by default) */
        :root {
            --bg-base: #0f172a;
            --bg-gradient: radial-gradient(circle at top left, #1e1b4b, #0f172a);
            --glass-bg: rgba(30, 41, 59, 0.7);
            --glass-border: rgba(255, 255, 255, 0.08);
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --accent-gradient: linear-gradient(135deg, #6366f1, #a855f7);
            --bubble-me: linear-gradient(135deg, #4f46e5, #7c3aed);
            --bubble-stranger: rgba(255, 255, 255, 0.1);
            --input-bg: rgba(15, 23, 42, 0.6);
        }

        /* 2. Explicit Light Mode Override */
        :root[data-theme="light"] {
            --bg-base: #f8fafc;
            --bg-gradient: radial-gradient(circle at top left, #e0e7ff, #f8fafc);
            --glass-bg: rgba(255, 255, 255, 0.8);
            --glass-border: rgba(0, 0, 0, 0.05);
            --text-primary: #0f172a;
            --text-secondary: #64748b;
            --bubble-me: linear-gradient(135deg, #6366f1, #8b5cf6);
            --bubble-stranger: #e2e8f0;
            --input-bg: rgba(255, 255, 255, 0.9);
        }

        /* 3. System Light Mode (Applies only if user hasn't forced Dark Mode) */
        @media (prefers-color-scheme: light) {
            :root:not([data-theme="dark"]) {
                --bg-base: #f8fafc;
                --bg-gradient: radial-gradient(circle at top left, #e0e7ff, #f8fafc);
                --glass-bg: rgba(255, 255, 255, 0.8);
                --glass-border: rgba(0, 0, 0, 0.05);
                --text-primary: #0f172a;
                --text-secondary: #64748b;
                --bubble-me: linear-gradient(135deg, #6366f1, #8b5cf6);
                --bubble-stranger: #e2e8f0;
                --input-bg: rgba(255, 255, 255, 0.9);
            }
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', system-ui, -apple-system, sans-serif; }

        /* Stable 100dvh layout */
        body { 
            background: var(--bg-gradient);
            background-color: var(--bg-base);
            color: var(--text-primary);
            height: 100dvh; 
            display: flex;
            justify-content: center;
            align-items: center;
            overflow: hidden;
            transition: background-color 0.3s, color 0.3s;
        }

        .app-container {
            display: flex;
            flex-direction: column;
            width: 100%;
            max-width: 900px;
            height: 100%;
            background: var(--glass-bg);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border-left: 1px solid var(--glass-border);
            border-right: 1px solid var(--glass-border);
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
            transition: background 0.3s, border-color 0.3s;
        }

        .header {
            padding: 20px 24px;
            border-bottom: 1px solid var(--glass-border);
            display: flex;
            justify-content: space-between;
            align-items: center;
            z-index: 10;
        }
        
        .header-left { display: flex; align-items: center; gap: 12px; }
        
        .header h1 { 
            font-size: 1.5rem; 
            font-weight: 800; 
            letter-spacing: -0.5px;
            background: var(--accent-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .theme-toggle {
            background: transparent;
            border: none;
            cursor: pointer;
            color: var(--text-secondary);
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 8px;
            border-radius: 50%;
            transition: background 0.2s, color 0.2s;
        }
        .theme-toggle:hover { background: var(--bubble-stranger); color: var(--text-primary); }
        .theme-toggle svg { width: 22px; height: 22px; fill: currentColor; }
        
        /* Specific override for the new stroke-based moon icon */
        .theme-toggle svg[fill="none"] { fill: none; stroke: currentColor; }

        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 999px;
            font-weight: 600;
            font-size: 0.9rem;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .btn:disabled { opacity: 0.4; cursor: not-allowed; transform: scale(1) !important; }
        .btn:active:not(:disabled) { transform: scale(0.95); }
        
        .btn-primary { 
            background: var(--accent-gradient); 
            color: white; 
            box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
        }
        
        .btn-secondary { background: var(--bubble-stranger); color: var(--text-primary); }

        #chatbox {
            flex-grow: 1;
            padding: 24px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 16px;
            scroll-behavior: smooth;
        }

        #chatbox::-webkit-scrollbar { width: 6px; }
        #chatbox::-webkit-scrollbar-thumb { background: var(--glass-border); border-radius: 10px; }

        .message-row { display: flex; width: 100%; animation: slideIn 0.3s ease-out forwards; }
        .message-row.me { justify-content: flex-end; }
        .message-row.stranger { justify-content: flex-start; }
        .message-row.system { justify-content: center; margin: 16px 0; }

        @keyframes slideIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .bubble {
            max-width: 80%;
            padding: 12px 18px;
            border-radius: 24px;
            word-wrap: break-word;
            line-height: 1.5;
            font-size: 0.95rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        }
        
        .me .bubble {
            background: var(--bubble-me);
            color: white;
            border-bottom-right-radius: 6px;
        }

        .stranger .bubble {
            background: var(--bubble-stranger);
            color: var(--text-primary);
            border-bottom-left-radius: 6px;
            border: 1px solid var(--glass-border);
        }

        .system .bubble {
            background: transparent;
            color: var(--text-secondary);
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 600;
            box-shadow: none;
            padding: 4px 12px;
            border: 1px solid var(--glass-border);
            border-radius: 999px;
        }

        .typing-indicator { display: none; align-items: center; gap: 6px; padding: 16px 20px !important; }
        .dot {
            width: 6px; height: 6px;
            background-color: var(--text-secondary);
            border-radius: 50%;
            animation: bounce 1.4s infinite ease-in-out both;
        }
        .dot:nth-child(1) { animation-delay: -0.32s; }
        .dot:nth-child(2) { animation-delay: -0.16s; }
        @keyframes bounce {
            0%, 80%, 100% { transform: scale(0); opacity: 0.4;}
            40% { transform: scale(1); opacity: 1;}
        }

        .input-area {
            padding: 16px 24px 24px 24px;
            background: transparent;
            display: flex;
            gap: 12px;
            z-index: 10;
        }
        
        .input-wrapper { flex-grow: 1; position: relative; display: flex; align-items: center; }

        #messageInput {
            width: 100%;
            padding: 16px 24px;
            border: 1px solid var(--glass-border);
            border-radius: 999px;
            background-color: var(--input-bg);
            color: var(--text-primary);
            outline: none;
            font-size: 1rem;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
            transition: border-color 0.3s, box-shadow 0.3s, background-color 0.3s, color 0.3s;
            backdrop-filter: blur(10px);
        }

        #messageInput:focus { border-color: #6366f1; box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2); }

        #sendBtn { border-radius: 50%; width: 50px; height: 50px; padding: 0; flex-shrink: 0; }
        .send-icon { width: 20px; height: 20px; fill: white; transform: translateX(2px); }

        @media (max-width: 600px) {
            .app-container { border-radius: 0; border: none; }
            .header { padding: 16px; }
            #chatbox { padding: 16px; }
            .input-area { padding: 12px 16px 16px 16px; }
        }
    </style>
</head>
<body>
    <div class="app-container">
        <div class="header">
            <div class="header-left">
                <h1>Elgemo</h1>
                <button id="themeToggle" class="theme-toggle" aria-label="Toggle theme"></button>
            </div>
            <div style="display: flex; gap: 8px;">
                <button id="startBtn" class="btn btn-primary">Find Match</button>
                <button id="skipBtn" class="btn btn-secondary" style="display: none;">Skip</button>
            </div>
        </div>
        
        <div id="chatbox">
            <div id="typingRow" class="message-row stranger" style="display: none;">
                <div class="bubble typing-indicator">
                    <div class="dot"></div><div class="dot"></div><div class="dot"></div>
                </div>
            </div>
        </div>
        
        <div class="input-area">
            <div class="input-wrapper">
                <input type="text" id="messageInput" placeholder="Type your message..." disabled autocomplete="off">
            </div>
            <button id="sendBtn" class="btn btn-primary" disabled>
                <svg class="send-icon" viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
            </button>
        </div>
    </div>

    <script>
        // --- 1. SAFE MOBILE KEYBOARD FIX ---
        if (window.visualViewport) {
            window.visualViewport.addEventListener('resize', () => {
                document.body.style.height = window.visualViewport.height + 'px';
                document.getElementById('chatbox').scrollTop = document.getElementById('chatbox').scrollHeight;
            });
        }
        
        document.getElementById('messageInput').addEventListener('focus', () => {
            setTimeout(() => {
                const chat = document.getElementById('chatbox');
                chat.scrollTop = chat.scrollHeight;
            }, 100);
        });

        // --- 2. THEME TOGGLE LOGIC ---
        const themeToggleBtn = document.getElementById('themeToggle');
        
        const sunIcon = `<svg viewBox="0 0 24 24"><path d="M12 7c-2.76 0-5 2.24-5 5s2.24 5 5 5 5-2.24 5-5-2.24-5-5-5zM2 13h2c.55 0 1-.45 1-1s-.45-1-1-1H2c-.55 0-1 .45-1 1s.45 1 1 1zm18 0h2c.55 0 1-.45 1-1s-.45-1-1-1h-2c-.55 0-1 .45-1 1s.45 1 1 1zM11 2v2c0 .55.45 1 1 1s1-.45 1-1V2c0-.55-.45-1-1-1s-1 .45-1 1zm0 18v2c0 .55.45 1 1 1s1-.45 1-1v-2c0-.55-.45-1-1-1s-1 .45-1 1zM5.99 4.58c-.39-.39-1.03-.39-1.41 0-.39.39-.39 1.03 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0s.39-1.03 0-1.41L5.99 4.58zm12.37 12.37c-.39-.39-1.03-.39-1.41 0-.39.39-.39 1.03 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0 .39-.39.39-1.03 0-1.41l-1.06-1.06zm1.06-10.96c.39-.39.39-1.03 0-1.41-.39-.39-1.03-.39-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41s1.03.39 1.41 0l1.06-1.06zM7.05 18.36c.39-.39.39-1.03 0-1.41-.39-.39-1.03-.39-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41s1.03.39 1.41 0l1.06-1.06z"/></svg>`;
        
        // Sleek, minimal Feather icon for the moon
        const moonIcon = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>`;

        // Apply saved theme immediately on load
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) { document.documentElement.setAttribute('data-theme', savedTheme); }

        function updateToggleIcon() {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const isSystemLight = window.matchMedia('(prefers-color-scheme: light)').matches;
            
            if (currentTheme === 'light' || (!currentTheme && isSystemLight)) {
                themeToggleBtn.innerHTML = moonIcon;
            } else {
                themeToggleBtn.innerHTML = sunIcon;
            }
        }
        
        updateToggleIcon();
        window.matchMedia('(prefers-color-scheme: light)').addEventListener('change', updateToggleIcon);

        themeToggleBtn.onclick = () => {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const isSystemLight = window.matchMedia('(prefers-color-scheme: light)').matches;
            
            let newTheme;
            if (currentTheme) {
                newTheme = currentTheme === 'light' ? 'dark' : 'light';
            } else {
                newTheme = isSystemLight ? 'dark' : 'light';
            }
            
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateToggleIcon();
        };

        // --- 3. CHAT LOGIC ---
        const socket = io(); 
        const chatbox = document.getElementById("chatbox");
        const messageInput = document.getElementById("messageInput");
        const typingRow = document.getElementById("typingRow");
        const startBtn = document.getElementById("startBtn");
        const skipBtn = document.getElementById("skipBtn");
        let typingTimeout;

        function printMessage(text, senderType) {
            const row = document.createElement("div");
            row.className = "message-row " + senderType;
            const bubble = document.createElement("div");
            bubble.className = "bubble";
            bubble.textContent = text;
            row.appendChild(bubble);
            chatbox.insertBefore(row, typingRow);
            chatbox.scrollTop = chatbox.scrollHeight;
        }

        function setUIState(inChat, searching = false) {
            startBtn.disabled = searching;
            if (inChat || searching) {
                startBtn.style.display = "none";
                skipBtn.style.display = "block";
            } else {
                startBtn.style.display = "block";
                skipBtn.style.display = "none";
                startBtn.innerText = "Find Match";
            }
            skipBtn.disabled = !inChat && !searching;
            messageInput.disabled = !inChat;
            document.getElementById("sendBtn").disabled = !inChat;
            if (!inChat) typingRow.style.display = "none";
            if (inChat) messageInput.focus();
        }

        function clearChat() {
            Array.from(chatbox.children).forEach(child => {
                if(child.id !== "typingRow") chatbox.removeChild(child);
            });
        }

        startBtn.onclick = () => {
            clearChat();
            socket.emit('start_search');
            setUIState(false, true); 
            printMessage("Looking for someone...", "system");
        };

        skipBtn.onclick = () => {
            clearChat();
            setUIState(false, true);
            printMessage("Looking for someone...", "system");
            socket.emit('skip');
        };

        function sendMessage() {
            if (messageInput.value.trim() !== "") {
                const text = messageInput.value;
                socket.emit('chat_message', { text: text });
                printMessage(text, "me");
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

        // Socket Events
        socket.on('system_message', (data) => printMessage(data.msg, "system"));
        socket.on('match_found', (data) => {
            clearChat();
            printMessage(`Connected with someone from ${data.country}`, "system");
            setUIState(true);
        });
        socket.on('chat_message', (data) => {
            typingRow.style.display = "none"; 
            printMessage(data.text, "stranger");
        });
        socket.on('typing', (data) => {
            typingRow.style.display = data.is_typing ? "flex" : "none";
            if(data.is_typing) chatbox.scrollTop = chatbox.scrollHeight;
        });
        socket.on('stranger_disconnected', () => {
            printMessage("Stranger has disconnected.", "system");
            setUIState(false); 
            startBtn.innerText = "Find New Match";
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
    country = request.headers.get("CF-IPCountry", "Unknown")
    user_data[session_id] = {"country": country}

@socketio.on('start_search')
def handle_search():
    session_id = request.sid
    global waiting_queue
    if session_id in user_rooms or session_id in waiting_queue: return
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

@socketio.on('chat_message')
def handle_message(data):
    session_id = request.sid
    current_time = time.time()
    last_time = user_last_message.get(session_id, 0)
    if current_time - last_time < RATE_LIMIT_SECONDS:
        emit('system_message', {'msg': 'You are sending messages too fast.'}, to=session_id)
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
    if session_id in user_data: del user_data[session_id]

def cleanup_user(session_id):
    global waiting_queue
    if session_id in waiting_queue: waiting_queue.remove(session_id)
    if session_id in user_last_message: del user_last_message[session_id]
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
    socketio.run(app, host="0.0.0.0", port=8000, debug=True)