import json
import mongo_service
import random
import string
from bson import json_util

def parse_json(data):
    return json.loads(json_util.dumps(data))

def generate_alphanumeric(length=6):
    # Combines letters (a-z, A-Z) and digits (0-9)
    characters = string.ascii_letters + string.digits
    
    # Randomly selects 6 characters from the pool
    return ''.join(random.choices(characters, k=length))

def create_game(name):
    code = generate_alphanumeric().upper()
    players = []
    players.append(name)
    scores = []
    scores.append({'name': name, 'score': 0})
    gameObj = {
        'gameId': code,
        'creator': name,
        'currentQuestion': None,
        'askedQuestions': [],
        'newQuestions': [],
        'players': players,
        'scores': scores,
        'guesses': []
    }
    mongo_service.insertIntoCollection("games", gameObj)
    jsonValue = {'gameId': code}
    return parse_json(jsonValue)

def get_game(gameId):
    query = {'gameId': gameId}
    game = mongo_service.findOneFromCollection("games", query)
    return parse_json(game)

def join_game(name, gameId):
    gameIdUpper = str(gameId).upper()
    game = get_game(gameIdUpper)
    players = game['players']
    players.append(name)
    game['players'] = players
    scores = game['scores']
    scores.append({'name': name, 'score': 0})
    game['scores'] = scores
    query = {'gameId': gameId}
    mongo_service.updateOne("games", game, query)
    return parse_json(game)

def add_question(questionAsker, questionText, gameId):
    query = {'gameId': gameId}
    game = mongo_service.findOneFromCollection("games", query)
    newQuestions = game['newQuestions']
    question = {
        'questionAsker': questionAsker,
        'questionText': questionText,
        'upvotes': 0,
        'downvotes': 0,
        'answers': [],
    }
    if (game['currentQuestion'] == None):
        game['currentQuestion'] = question
    else:
        newQuestions.append(question)
        game['newQuestions'] = newQuestions
    mongo_service.updateOne("games", game, query)
    return parse_json(game)

def add_answer(answerName, answerText, gameId):
    query = {'gameId': gameId}
    game = mongo_service.findOneFromCollection("games", query)
    currentQuestion = game['currentQuestion']
    answer = {
        'answerName': answerName,
        'answerText': answerText,
        'upvotes': 0,
        'downvotes': 0
    }
    currentQuestion['answers'].append(answer)
    game['currentQuestion'] = currentQuestion
    mongo_service.updateOne("games", game, query)
    return parse_json(game)

def add_guess(guessName, userName, gameId):
    query = {'gameId': gameId}
    game = mongo_service.findOneFromCollection("games", query)
    guess = {
        'guessName': guessName,
        'userName': userName
    }
    game['guesses'].append(guess)
    mongo_service.updateOne("games", game, query)
    return parse_json(game)

def next_question(gameId):
    query = {'gameId': gameId}
    game = mongo_service.findOneFromCollection("games", query)
    formerQuestion = game['currentQuestion']
    askedQuestions = game['askedQuestions']
    newQuestions = game['newQuestions']
    scores = game['scores']
    guesses = game['guesses']

    for score in scores:
        for answer in formerQuestion['answers']:
            if answer['answerName'] == score['name']:
                score['score'] = score['score'] + answer['upvotes']

    for guess in guesses:
        if guess['guessName'] == formerQuestion['questionAsker']:
            for score in scores:
                if guess['userName'] == score['name']:
                    score['score'] = score['score'] + 1

    askedQuestions.append(formerQuestion)
    currentQuestion = random.choice(newQuestions)
    newQuestions.remove(currentQuestion)

    game['currentQuestion'] = currentQuestion
    game['askedQuestions'] = askedQuestions
    game['newQuestions'] = newQuestions
    game['scores'] = scores
    game['guesses'] = []
    mongo_service.updateOne("games", game, query)
    return parse_json(game)

def vote_question(gameId, vote):
    query = {'gameId': gameId}
    game = mongo_service.findOneFromCollection("games", query)
    currentQuestion = game['currentQuestion']
    if (vote == 'up'):
        vote = currentQuestion['upvotes']
        vote = vote + 1
        currentQuestion['upvotes'] = vote
    else:
        vote = currentQuestion['downvotes']
        vote = vote + 1
        currentQuestion['downvotes'] = vote
    game['currentQuestion'] = currentQuestion
    mongo_service.updateOne("games", game, query)
    return game

def vote_answer(gameId, vote, name):
    query = {'gameId': gameId}
    game = mongo_service.findOneFromCollection("games", query)
    currentQuestion = game['currentQuestion']
    for answer in currentQuestion['answers']:
        if answer['answerName'] == name:
            if (vote == 'up'):
                vote = answer['upvotes']
                vote = vote + 1
                answer['upvotes'] = vote
            else:
                vote = answer['downvotes']
                vote = vote + 1
                answer['downvotes'] = vote
    game['currentQuestion'] = currentQuestion
    mongo_service.updateOne("games", game, query)
    return game
