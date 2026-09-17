from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, leave_room, emit
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'pizzachat_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('join_room')
def handle_join(data):
    username = data.get('username', 'Anonimo')
    room = data.get('room', 'stanza1')
    
    # Rimuove l'utente dalle altre stanze tranne la propria sessione
    for r in list(socketio.server.rooms(request.sid)):
        if r != request.sid:
            leave_room(r)

    join_room(room)
    
    emit('receive_message', {
        'message': f"{username} è entrato nella stanza {room}.",
        'is_system': True
    }, to=room)

@socketio.on('send_message')
def handle_message(data):
    username = data.get('username', 'Anonimo')
    message = data.get('message', '')
    room = data.get('room', 'stanza1')
    now = datetime.now().strftime("%H:%M")

    # Invia il messaggio a TUTTI quelli nella stanza (incluso chi lo ha inviato)
    emit('receive_message', {
        'username': username,
        'message': message,
        'time': now,
        'is_system': False
    }, to=room)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)