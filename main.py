import os
import uuid
import time
from flask import Flask, request
from flask_socketio import SocketIO, join_room, leave_room, emit, disconnect
from better_profanity import profanity 
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
socketio = SocketIO(app, cors_allowed_origins="*")

profanity.load_censor_words() 

VERSION = "1.0.3"

# ==========================================
# FRONTEND: HTML/CSS/JS (Elgemo v1.0.3)
# ==========================================
HTML_PAGE = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <title>Elgemo</title>
    <script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
    <style>
        :root {{
            --bg-base: #000000; 
            --bg-gradient: #000000; 
            --glass-bg: rgba(12, 12, 12, 0.85); 
            --glass-border: rgba(255, 255, 255, 0.08); 
            --text-primary: #ffffff;
            --text-secondary: #a3a3a3;
            --accent-gradient: linear-gradient(135deg, #ef4444, #f97316); 
            --bubble-me: linear-gradient(135deg, #ea580c, #dc2626);
            --bubble-stranger: rgba(255, 255, 255, 0.12);
            --input-bg: rgba(10, 10, 10, 0.8);
            --focus-ring: rgba(234, 88, 12, 0.25);
            --focus-border: #ea580c;
        }}

        :root[data-theme="light"] {{
            --bg-base: #f5f5f5;
            --bg-gradient: radial-gradient(circle at top left, #ffffff, #f5f5f5);
            --glass-bg: rgba(255, 255, 255, 0.9);
            --glass-border: rgba(0, 0, 0, 0.1);
            --text-primary: #0a0a0a;
            --text-secondary: #525252;
            --bubble-me: linear-gradient(135deg, #ea580c, #dc2626);
            --bubble-stranger: #e5e5e5;
            --input-bg: rgba(255, 255, 255, 1);
            --focus-ring: rgba(234, 88, 12, 0.2);
            --focus-border: #ea580c;
        }}

        * {{ 
            box-sizing: border-box; 
            margin: 0; 
            padding: 0; 
            font-family: 'Inter', system-ui, -apple-system, sans-serif; 
        }}

        body, html {{
            width: 100%;
            /* Prevent elastic bounce on mobile */
            overscroll-behavior-y: none; 
        }}

        body {{ 
            background: var(--bg-gradient);
            background-color: var(--bg-base);
            color: var(--text-primary);
            /* Fallback height, will be overwritten by JS visualViewport */
            height: 100vh; 
            display: flex;
            justify-content: center;
            align-items: center;
            overflow: hidden;
            transition: background-color 0.4s ease, color 0.4s ease;
        }}

        .app-container {{
            position: relative;
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
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.3);
            transition: background 0.4s ease, border-color 0.4s ease;
        }}

        .modal-overlay {{
            position: absolute;
            inset: 0;
            background: rgba(0, 0, 0, 0.6);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 100;
            border-radius: inherit;
            transition: opacity 0.3s ease;
        }}

        .modal-content {{
            background: var(--glass-bg);
            border: 1px solid var(--glass-border);
            padding: 32px;
            border-radius: 20px;
            max-width: 420px;
            width: 90%;
            box-shadow: 0 20px 40px rgba(0,0,0,0.4);
            animation: slideInUp 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }}

        .modal-content h2 {{
            margin-bottom: 20px;
            font-size: 1.5rem;
            font-weight: 800;
            background: var(--accent-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .cautions-list {{
            margin-left: 20px;
            color: var(--text-secondary);
            line-height: 1.6;
            font-size: 0.95rem;
        }}

        .cautions-list li {{ margin-bottom: 14px; }}
        .cautions-list strong {{ color: var(--text-primary); }}

        .header {{
            padding: 20px 24px;
            border-bottom: 1px solid var(--glass-border);
            display: flex;
            justify-content: space-between;
            align-items: center;
            z-index: 10;
        }}
        
        .header-left {{ display: flex; align-items: center; gap: 14px; }}
        
        .header h1 {{ 
            font-size: 1.5rem; 
            font-weight: 800; 
            letter-spacing: -0.5px;
            background: var(--accent-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .online-badge {{
            background: rgba(34, 197, 94, 0.15);
            color: #22c55e;
            border: 1px solid rgba(34, 197, 94, 0.3);
            padding: 4px 10px;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 6px;
            white-space: nowrap;
        }}

        :root[data-theme="light"] .online-badge {{
            background: rgba(34, 197, 94, 0.1);
            color: #16a34a;
            border-color: rgba(34, 197, 94, 0.3);
        }}

        .online-badge::before {{
            content: "";
            display: block;
            width: 6px;
            height: 6px;
            background-color: currentColor;
            border-radius: 50%;
            box-shadow: 0 0 6px currentColor;
            animation: pulse 2s infinite;
        }}

        @keyframes pulse {{
            0% {{ opacity: 0.5; }}
            50% {{ opacity: 1; }}
            100% {{ opacity: 0.5; }}
        }}

        .theme-toggle {{
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
        }}
        .theme-toggle:hover {{ background: var(--bubble-stranger); color: var(--text-primary); }}
        .theme-toggle svg {{ width: 22px; height: 22px; fill: currentColor; }}

        .btn {{
            padding: 10px 24px;
            border: none;
            border-radius: 999px;
            font-weight: 600;
            font-size: 0.9rem;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .btn:disabled {{ opacity: 0.4; cursor: not-allowed; transform: scale(1) !important; }}
        .btn:hover:not(:disabled) {{ transform: translateY(-1px); box-shadow: 0 6px 20px rgba(0,0,0,0.2); }}
        .btn:active:not(:disabled) {{ transform: scale(0.95); box-shadow: none; }}
        
        .btn-primary {{ background: var(--accent-gradient); color: white; box-shadow: 0 4px 15px rgba(234, 88, 12, 0.25); }}
        .btn-secondary {{ background: var(--bubble-stranger); color: var(--text-primary); border: 1px solid var(--glass-border); }}

        #chatbox {{
            flex-grow: 1;
            padding: 24px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 16px;
            scroll-behavior: smooth;
            position: relative;
        }}

        #chatbox::-webkit-scrollbar {{ width: 6px; }}
        #chatbox::-webkit-scrollbar-thumb {{ background: var(--glass-border); border-radius: 10px; }}

        .version-label {{
            position: absolute;
            bottom: 8px;
            right: 12px;
            font-size: 10px;
            color: var(--text-secondary);
            opacity: 0.5;
            pointer-events: none;
            font-weight: 500;
        }}

        .message-row {{ display: flex; width: 100%; animation: slideInUp 0.3s ease-out forwards; }}
        .message-row.me {{ justify-content: flex-end; }}
        .message-row.stranger {{ justify-content: flex-start; }}
        .message-row.system {{ justify-content: center; margin: 16px 0; }}

        @keyframes slideInUp {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}

        .bubble {{
            max-width: 80%;
            padding: 12px 18px;
            border-radius: 24px;
            word-wrap: break-word;
            line-height: 1.5;
            font-size: 0.95rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        .me .bubble {{ background: var(--bubble-me); color: white; border-bottom-right-radius: 6px; }}
        .stranger .bubble {{ background: var(--bubble-stranger); color: var(--text-primary); border-bottom-left-radius: 6px; border: 1px solid var(--glass-border); }}
        .system .bubble {{ background: transparent; color: var(--text-secondary); font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; box-shadow: none; padding: 4px 12px; border: 1px solid var(--glass-border); border-radius: 999px; }}

        .typing-indicator {{ display: none; align-items: center; gap: 6px; padding: 16px 20px !important; }}
        .dot {{ width: 6px; height: 6px; background-color: var(--text-secondary); border-radius: 50%; animation: bounce 1.4s infinite ease-in-out both; }}
        .dot:nth-child(1) {{ animation-delay: -0.32s; }}
        .dot:nth-child(2) {{ animation-delay: -0.16s; }}
        @keyframes bounce {{ 0%, 80%, 100% {{ transform: scale(0); opacity: 0.4;}} 40% {{ transform: scale(1); opacity: 1;}} }}

        .input-area {{
            padding: 16px 24px 24px 24px;
            padding-bottom: max(24px, env(safe-area-inset-bottom));
            background: transparent;
            display: flex;
            gap: 12px;
            z-index: 10;
        }}
        
        .input-wrapper {{ flex-grow: 1; position: relative; display: flex; align-items: center; }}

        #messageInput {{
            width: 100%;
            padding: 16px 24px;
            border: 1px solid var(--glass-border);
            border-radius: 999px;
            background-color: var(--input-bg);
            color: var(--text-primary);
            outline: none;
            font-size: 1rem;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.2);
            transition: border-color 0.3s, box-shadow 0.3s, background-color 0.3s, color 0.3s;
            backdrop-filter: blur(10px);
            -webkit-appearance: none; 
        }}

        #messageInput:focus {{ border-color: var(--focus-border); box-shadow: 0 0 0 3px var(--focus-ring); }}

        #sendBtn {{ border-radius: 50%; width: 50px; height: 50px; padding: 0; flex-shrink: 0; }}
        .send-icon {{ width: 20px; height: 20px; fill: white; transform: translateX(2px); }}

        @media (max-width: 600px) {{
            .app-container {{ border-radius: 0; border: none; }}
            .header {{ padding: 16px; }}
            #chatbox {{ padding: 16px; }}
            
            .input-area {{ 
                padding: 12px 16px max(16px, env(safe-area-inset-bottom)) 16px; 
            }}

            #messageInput {{
                padding: 12px 20px;
                font-size: 16px !important; /* Prevent iOS zoom */
            }}
            
            #sendBtn {{ width: 44px; height: 44px; }}
            .send-icon {{ width: 18px; height: 18px; }}
        }}
    </style>
</head>
<body>
    <div class="app-container">
        <div id="welcomeModal" class="modal-overlay">
            <div class="modal-content">
                <h2>Welcome to Elgemo</h2>
                <ul class="cautions-list">
                    <li><strong>No Profanity:</strong> Using explicit language 3 times will trigger an automatic 5-minute IP ban.</li>
                    <li><strong>Stay Safe:</strong> Do not share personal information, links, or contact details.</li>
                    <li><strong>Be Respectful:</strong> Treat your chat partners with kindness and respect.</li>
                </ul>
                <button id="acceptRulesBtn" class="btn btn-primary" style="width: 100%; margin-top: 24px; padding: 14px;">I Understand</button>
            </div>
        </div>

        <div class="header">
            <div class="header-left">
                <h1>Elgemo</h1>
                <span id="onlineCount" class="online-badge">1 Online</span>
                <button id="themeToggle" class="theme-toggle" aria-label="Toggle theme"></button>
            </div>
            <div>
                <button id="actionBtn" class="btn btn-primary">Find Match</button>
            </div>
        </div>
        
        <div id="chatbox">
            <div id="typingRow" class="message-row stranger" style="display: none;">
                <div class="bubble typing-indicator">
                    <div class="dot"></div><div class="dot"></div><div class="dot"></div>
                </div>
            </div>
            <div class="version-label">v{VERSION}</div>
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
        const socket = io(); 
        const chatbox = document.getElementById("chatbox");
        const messageInput = document.getElementById("messageInput");
        const typingRow = document.getElementById("typingRow");
        const actionBtn = document.getElementById("actionBtn");
        const onlineCountEl = document.getElementById("onlineCount");
        const sendBtn = document.getElementById("sendBtn");
        
        let currentState = "IDLE"; 
        let typingTimeout;

        // ==========================================
        // THE DEFINITIVE MOBILE KEYBOARD FIX
        // ==========================================
        if (window.visualViewport) {{
            const adjustAppHeight = () => {{
                // Force the body height to exactly match the visible screen space
                document.body.style.height = `${{window.visualViewport.height}}px`;
                // Keep the chat scrolled to the bottom
                chatbox.scrollTop = chatbox.scrollHeight;
            }};
            
            // Listen for the keyboard popping up or dismissing
            window.visualViewport.addEventListener('resize', adjustAppHeight);
            
            // Set initial height
            adjustAppHeight();
        }}
        // ==========================================

        function updateUI(state) {{
            currentState = state;
            switch(state) {{
                case "IDLE":
                    actionBtn.innerText = "Find Match";
                    actionBtn.className = "btn btn-primary";
                    actionBtn.disabled = false;
                    messageInput.disabled = true;
                    sendBtn.disabled = true;
                    typingRow.style.display = "none";
                    break;
                case "SEARCHING":
                    actionBtn.innerText = "Stop";
                    actionBtn.className = "btn btn-secondary";
                    actionBtn.disabled = false;
                    messageInput.disabled = true;
                    sendBtn.disabled = true;
                    break;
                case "CHATTING":
                    actionBtn.innerText = "Stop";
                    actionBtn.className = "btn btn-secondary";
                    actionBtn.disabled = false;
                    messageInput.disabled = false;
                    sendBtn.disabled = false;
                    messageInput.focus();
                    break;
            }}
        }}

        actionBtn.onclick = () => {{
            if (currentState === "IDLE") {{
                clearChat();
                socket.emit('start_search');
                printMessage("Looking for someone...", "system");
                updateUI("SEARCHING");
            }} else {{
                socket.emit('skip'); 
                printMessage("Session stopped.", "system");
                updateUI("IDLE");
            }}
        }};

        function printMessage(text, senderType) {{
            const row = document.createElement("div");
            row.className = "message-row " + senderType;
            const bubble = document.createElement("div");
            bubble.className = "bubble";
            bubble.textContent = text;
            row.appendChild(bubble);
            chatbox.insertBefore(row, typingRow);
            chatbox.scrollTop = chatbox.scrollHeight;
        }}

        function clearChat() {{
            Array.from(chatbox.children).forEach(child => {{
                if(child.id !== "typingRow" && !child.classList.contains('version-label')) {{
                    chatbox.removeChild(child);
                }}
            }});
        }}

        function sendMessage() {{
            if (messageInput.value.trim() !== "") {{
                const text = messageInput.value;
                socket.emit('chat_message', {{ text: text }});
                printMessage(text, "me"); 
                messageInput.value = "";
                socket.emit('typing', {{ is_typing: false }});
            }}
        }}

        sendBtn.onclick = sendMessage;
        
        messageInput.addEventListener("keypress", (e) => {{
            if (e.key === "Enter") sendMessage();
        }});
        
        messageInput.addEventListener("input", () => {{
            socket.emit('typing', {{ is_typing: true }});
            clearTimeout(typingTimeout);
            typingTimeout = setTimeout(() => {{
                socket.emit('typing', {{ is_typing: false }});
            }}, 1500);
        }});

        // Socket Events
        socket.on('user_count', (data) => {{ onlineCountEl.innerText = `${{data.count}} Online`; }});
        
        socket.on('match_found', (data) => {{
            clearChat();
            printMessage(`Connected with someone from ${{data.country}}`, "system");
            updateUI("CHATTING");
        }});
        
        socket.on('chat_message', (data) => {{
            typingRow.style.display = "none"; 
            printMessage(data.text, "stranger");
        }});
        
        socket.on('typing', (data) => {{
            typingRow.style.display = data.is_typing ? "flex" : "none";
            if(data.is_typing) chatbox.scrollTop = chatbox.scrollHeight;
        }});
        
        socket.on('stranger_disconnected', () => {{
            printMessage("Stranger has disconnected.", "system");
            updateUI("IDLE"); 
        }});
        
        socket.on('system_message', (data) => printMessage(data.msg, "system"));
        
        socket.on('banned', (data) => {{
            printMessage(data.msg, "system");
            updateUI("IDLE");
            actionBtn.disabled = true;
            socket.disconnect(); 
        }});

        // Modal Logic
        document.getElementById('acceptRulesBtn').addEventListener('click', () => {{
            const modal = document.getElementById('welcomeModal');
            modal.style.opacity = '0';
            setTimeout(() => {{ modal.style.display = 'none'; }}, 300);
        }});
        
        // Theme Toggle Logic
        const themeToggleBtn = document.getElementById('themeToggle');
        const sunIcon = `<svg viewBox="0 0 24 24"><path d="M12 7c-2.76 0-5 2.24-5 5s2.24 5 5 5 5-2.24 5-5-2.24-5-5-5zM2 13h2c.55 0 1-.45 1-1s-.45-1-1-1H2c-.55 0-1 .45-1 1s.45 1 1 1zm18 0h2c.55 0 1-.45 1-1s-.45-1-1-1h-2c-.55 0-1 .45-1 1s.45 1 1 1zM11 2v2c0 .55.45 1 1 1s1-.45 1-1V2c0-.55-.45-1-1-1s-1 .45-1 1zm0 18v2c0 .55.45 1 1 1s1-.45 1-1v-2c0-.55-.45-1-1-1s-1 .45-1 1zM5.99 4.58c-.39-.39-1.03-.39-1.41 0-.39.39-.39 1.03 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0s.39-1.03 0-1.41L5.99 4.58zm12.37 12.37c-.39-.39-1.03-.39-1.41 0-.39.39-.39 1.03 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0 .39-.39.39-1.03 0-1.41l-1.06-1.06zm1.06-10.96c.39-.39.39-1.03 0-1.41-.39-.39-1.03-.39-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41s1.03.39 1.41 0l1.06-1.06zM7.05 18.36c.39-.39.39-1.03 0-1.41-.39-.39-1.03-.39-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41s1.03.39 1.41 0l1.06-1.06z"/></svg>`;
        const moonIcon = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>`;

        function updateToggleIcon() {{
            const currentTheme = document.documentElement.getAttribute('data-theme');
            themeToggleBtn.innerHTML = currentTheme === 'light' ? moonIcon : sunIcon;
        }}

        themeToggleBtn.onclick = () => {{
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateToggleIcon();
        }};

        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) {{
            document.documentElement.setAttribute('data-theme', savedTheme);
        }} else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {{
            document.documentElement.setAttribute('data-theme', 'light');
        }}
        
        updateToggleIcon();
    </script>
</body>
</html>
"""

# ==========================================
# WEBSOCKET STATE & LOGIC
# ==========================================
waiting_queue = []
user_data = {}  
user_rooms = {} 
user_last_message = {} 
banned_ips = {} 
RATE_LIMIT_SECONDS = 0.5 

def get_client_ip():
    return request.headers.get('CF-Connecting-IP', request.headers.get('X-Forwarded-For', request.remote_addr))

@socketio.on('connect')
def handle_connect():
    ip = get_client_ip()
    if ip in banned_ips and time.time() < banned_ips[ip]:
        emit('banned', {'msg': 'Connection refused: Your IP is temporarily banned.'})
        disconnect()
        return False
    session_id = request.sid
    user_data[session_id] = {"country": request.headers.get("CF-IPCountry", "Unknown"), "ip": ip, "strikes": 0}
    emit('user_count', {'count': len(user_data)}, broadcast=True)

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
        raw_text = data.get('text', '')
        clean_text = profanity.censor(raw_text)
        if raw_text != clean_text:
            user_data[session_id]["strikes"] += 1
            if user_data[session_id]["strikes"] >= 3:
                ip = user_data[session_id]["ip"]
                banned_ips[ip] = time.time() + 300 
                emit('banned', {'msg': 'You have been banned for 5 minutes due to profanity.'}, to=session_id)
                partner_id = next((sid for sid, rid in user_rooms.items() if rid == room_id and sid != session_id), None)
                if partner_id: emit('system_message', {'msg': 'We disconnected the user to maintain good service.'}, to=partner_id)
                disconnect()
                return
        emit('chat_message', {'text': clean_text}, to=room_id, include_self=False)

@socketio.on('typing')
def handle_typing(data):
    if request.sid in user_rooms:
        emit('typing', {'is_typing': data['is_typing']}, to=user_rooms[request.sid], include_self=False)

@socketio.on('skip')
def handle_skip():
    cleanup_user(request.sid)

@socketio.on('disconnect')
def handle_disconnect():
    session_id = request.sid
    cleanup_user(session_id)
    if session_id in user_data: 
        del user_data[session_id]
        emit('user_count', {'count': len(user_data)}, broadcast=True)

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

@app.route('/')
def index(): 
    return HTML_PAGE

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    socketio.run(app, host="0.0.0.0", port=port, debug=debug)