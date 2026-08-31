import json
from bson import json_util
import mongo_service
import character_scraper
import random

def parse_json(data):
    return json.loads(json_util.dumps(data))

def submit_battle(battleParams):
    # generate new chars ELO
    winner = 1 if battleParams['fighter1']['ID'] == battleParams['winner']['ID'] else 2
    fighter1ELO, fighter2ELO = calculate_elo(battleParams['fighter1']['score'], battleParams['fighter2']['score'], winner, battleParams['score'])

    fighter1Query = {'ID': battleParams['fighter1']['ID']}
    fighter1 = mongo_service.findOneFromCollection("Characters", fighter1Query)
    fighter1Change = fighter1['score'] - fighter1ELO
    fighter1['score'] = fighter1ELO
    mongo_service.updateOne("Characters", fighter1, {"ID": battleParams['fighter1']['ID']})

    fighter2Query = {'ID': battleParams['fighter2']['ID']}
    fighter2 = mongo_service.findOneFromCollection("Characters", fighter2Query)
    fighter2Change = fighter2['score'] - fighter2ELO
    fighter2['score'] = fighter2ELO
    mongo_service.updateOne("Characters", fighter2, {"ID": battleParams['fighter2']['ID']})


    # limit data sent to mongo for each fighter
    fighter1BattlesObj = {
        'ID': battleParams['fighter1']['ID'],
        'name': battleParams['fighter1']['Name'],
        'score': battleParams['fighter1']['score'],
        'img_src': battleParams['fighter1']['img_src'],
        'scoreChange': fighter1Change
    }

    fighter2BattlesObj = {
        'ID': battleParams['fighter2']['ID'],
        'name': battleParams['fighter2']['Name'],
        'score': battleParams['fighter2']['score'],
        'img_src': battleParams['fighter2']['img_src'],
        'scoreChange': fighter2Change
    }

    battleParams['fighter1'] = fighter1BattlesObj
    battleParams['fighter2'] = fighter2BattlesObj

    mongo_service.insertIntoCollection('Battles', battleParams)

    obj = {
        'fighter1': fighter1,
        'fighter2': fighter2
    }

    return parse_json(obj)

def get_rankings(rankingParams):
    rankingsList = mongo_service.get_rankings(rankingParams)
    return parse_json(rankingsList)

def get_battles_results(battleParams):
    battlesList = mongo_service.get_battles_results(battleParams)
    return parse_json(battlesList)

def get_top_10_battles(count):
    battlesList = mongo_service.get_top_10_chacters(count)
    random.shuffle(battlesList)
    battles= []
    rangeVal = int(len(battlesList)/2)
    for i in range(0, rangeVal):
        val = {
            "fighter1": battlesList[i],
            "fighter2": battlesList[i+rangeVal]
        }
        i = i + 2
        battles.append(val)
    return parse_json(battles)

def get_5_random_battles(count):
    random_number = random.randint(1, 9999)
    battlesList = mongo_service.get_10_closest_characters(random_number, count)
    random.shuffle(battlesList)
    battles= []
    rangeVal = int(len(battlesList)/2)
    for i in range(0, rangeVal):
        val = {
            "fighter1": battlesList[i],
            "fighter2": battlesList[i+rangeVal]
        }
        i = i + 2
        battles.append(val)
    return parse_json(battles)

def scrape_character(url):
    response = character_scraper.scrape_single_character(url)
    return parse_json(response)

def get_animes_list():
    response = mongo_service.get_animes_list()
    return parse_json(response)

def calculate_elo(f1_elo, f2_elo, winner, score):
    # Clamp score between 1 and 10
    score = max(1, min(10, score))

    # Expected scores
    expected_f1 = 1 / (1 + 10 ** ((f2_elo - f1_elo) / 400))
    expected_f2 = 1 / (1 + 10 ** ((f1_elo - f2_elo) / 400))

    # Actual results
    if winner == 1:
        actual_f1 = 1
        actual_f2 = 0
    elif winner == 2:
        actual_f1 = 0
        actual_f2 = 1
    else:
        raise ValueError("winner must be 1 or 2")

    # Dynamic K-factor (scaled by dominance)
    base_k = 32
    k = base_k * (0.5 + score / 10)  
    # score=1 → K ≈ 19.2 (small change)
    # score=10 → K ≈ 48 (large change)

    # Update ELO
    new_f1_elo = f1_elo + k * (actual_f1 - expected_f1)
    new_f2_elo = f2_elo + k * (actual_f2 - expected_f2)

    return round(new_f1_elo, 2), round(new_f2_elo, 2)
