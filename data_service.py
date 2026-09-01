import json
import mongo_service
import random
import string

def parse_json(data):
    return json.loads(json_util.dumps(data))

def generate_alphanumeric(length=6):
    # Combines letters (a-z, A-Z) and digits (0-9)
    characters = string.ascii_letters + string.digits
    
    # Randomly selects 6 characters from the pool
    return ''.join(random.choices(characters, k=length))

def create_game(name):
    code = generate_alphanumeric()
    gameObj = {
        'gameId': code,
        'creator': name,
        'currentQuestion': None,
        'askedQuestions': [],
        'newQuestions': []
    }
    mongo_service.insertIntoCollection("games", gameObj)
    return code

def get_game(gameId):
    query = {'gameId': gameId}
    game = mongo_service.findOneFromCollection("games", query)
    return parse_json(game)

def join_game(name, gameId):
    return get_game(gameId)

def add_question(questionAsker, questionText, gameId):
    query = {'gameId': gameId}
    game = mongo_service.findOneFromCollection("games", query)
    newQuestions = game['newQuestions']
    question = {
        'questionAsker': questionAsker,
        'questionText': questionText
    }
    newQuestions.append(question)
    game['newQuestions'] = newQuestions
    mongo_service.updateOne("games", game, query)
    return parse_json(game)

def next_question(gameId):
    query = {'gameId': gameId}
    game = mongo_service.findOneFromCollection("games", query)
    formerQuestion = game['currentQuestion']
    askedQuestions = game['askedQuestions']
    newQuestions = game['newQuestions']
    askedQuestions.append(formerQuestion)
    currentQuestion = random.choice(newQuestions)
    newQuestions.remove(currentQuestion)
    game['currentQuestion'] = currentQuestion
    game['askedQuestions'] = askedQuestions
    game['newQuestions'] = newQuestions
    mongo_service.updateOne("games", game, query)
    return parse_json(game)

