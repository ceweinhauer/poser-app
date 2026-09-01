from flask import Flask, request
from flask_cors import CORS
import data_service
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def status_ping():
    return 'Poser App'
    
@app.route('/games', methods=['POST'])
def create_game():
    if request.method == 'POST':
            name = request.json['creatorName']
            code = data_service.create_game(name)
            return code

@app.route('/games/<gameId>', methods=['GET'])
def get_game(gameId):
    return data_service.get_game(gameId)

@app.route('/games/join', methods=['POST'])
def join_game():
    if request.method == 'POST':
            name = request.json['name']
            gameId = request.json['gameId']
            game = data_service.join_game(name, gameId)
            return game

@app.route('/games/add_question', methods=['POST'])
def add_question():
    if request.method == 'POST':
            questionAsker = request.json['questionAsker']
            questionText = request.json['questionText']
            gameId = request.json['gameId']
            game = data_service.add_question(questionAsker, questionText, gameId)
            return game

@app.route('/games/next', methods=['POST'])
def next_question():
    if request.method == 'POST':
            gameId = request.json['gameId']
            game = data_service.next_question(gameId)
            return game

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)