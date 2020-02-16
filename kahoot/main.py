from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
from random import randint
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'
socketio = SocketIO(app)

def random_digit(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/session')
def session():
    return render_template('session.html')

@app.route('/criar')
def criar():
    return render_template('criar.html')

quests = {}

@app.route('/api/entrar', methods=['POST'])
def api_entrar():
    entrar = int(request.values.get('key'))
    meu_id = request.values.get('id')
    meu_nome = request.values.get('nome')
    if entrar in quests:
        if quests[entrar]['status'] == 'wait':
            quests[entrar]['conectados'][meu_id] = meu_nome;
            print(quests)
            socketio.emit('quest', {'action': 'add', 'name': meu_nome}, room=quests[entrar]['id'])
            return jsonify({"status": "200"}), 200
    return jsonify({"status": "500"}), 500
    

@app.route('/api/criar', methods=['POST'])
def api_criar():
    try:
        print("--------------------------------------")
        key = random_digit(6)
        if key in quests:
            while key in quests:
                key = random_digit(6)

        user_id = request.values.get('id')
        quest = json.loads(request.values.get('quest'))
        quests[key] = {
            'status': 'wait',
            'id': user_id,
            'quest': quest,
            'conectados': {}
        }
        socketio.emit('my response', {'msg': "nomeeee" + ' has entered the room.'}, room=user_id)
        return jsonify({"status": "200", "key": key}), 200

    except:
        return jsonify({"status": "500"}), 500



def messageReceived(methods=['GET', 'POST']):
    print('message was received!!!')


@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    print('received my event: ' + str(json))
    print("REQUEST:::::::" + request.sid)
    socketio.emit('my response', json, callback=messageReceived)

@socketio.on('create_quest')
def create_my_quest(json, methods=['GET', 'POST']):
    print('received my event: ' + str(json))
    socketio.emit('my response', json, callback=messageReceived)

@socketio.on('disconnect')
def desconecta():
    print("DESCONECTOUUUUU")
    print(request.sid)
    for i in quests:
        if request.sid in quests[i]['conectados']:
            socketio.emit('quest', {'action': 'rem', 'name': quests[i]['conectados'][request.sid]}, room=quests[i]['id'])


if __name__ == '__main__':
    socketio.run(app, debug=True)
