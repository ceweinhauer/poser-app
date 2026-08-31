from flask import Flask, request
from flask_cors import CORS
import data_service
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def status_ping():
    return 'Anime PowerScaler'

@app.route('/login/<username>/<password>', methods=['GET'])
def login(username, password):
    return data_service.login(username, password)

@app.route('/submit_battle', methods=['POST'])
def submit_battle():
    if request.method == 'POST':
        battleObj = request.json
        results = data_service.submit_battle(battleObj)
        return results
    
@app.route('/get_rankings', methods=['POST'])
def getRankings():
    if request.method == 'POST':
        rankingParams = request.json
        results = data_service.get_rankings(rankingParams)
        return results
    
@app.route('/get_battles_results', methods=['POST'])
def getBattlesResults():
    if request.method == 'POST':
        battleParams = request.json
        results = data_service.get_battles_results(battleParams)
        return results
    
@app.route('/get_battles/<type>/<count>', methods=['GET'])
def get_battles(type, count):
    if type == 'top':
        return data_service.get_top_10_battles(count)
    elif type == 'random':
        return data_service.get_5_random_battles(count)

@app.route('/scrape_character/<id>/', methods=['GET'])
def scrape_character(id):
    return data_service.scrape_character(id)

@app.route('/get_animes_list', methods=['GET'])
def get_animes_list():
    return data_service.get_animes_list()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)