from flask import Flask
from flask_ask import Ask, question, statement
import logging
import redis
import json
import os


app = Flask(__name__)
ask = Ask(app, "/")
logger = logging.getLogger('flask_ask').setLevel(logging.DEBUG)

# Initialize redis client
REDIS_HOST = os.environ.get('REDIS_HOST')
if REDIS_HOST == None:
    logger.info("No REDIS_HOST environment variable set.")
REDIS_PORT = os.environ.get('REDIS_PORT')
if REDIS_PORT == None:
    logger.info("No REDIS_PORT environment variable set.")
redis_client = redis.StrictRedis(host=REDIS_HOST, port=int(REDIS_PORT), db=0)

MAX_PLAYERS = os.environ.get('MAX_PLAYERS', 4)
REDIS_SET_NAME = "Mcnulty"


@ask.launch
def launch():
    speech_output = "Ready to play 301?"
    reprompt_text = "Set up a game by saying start a game with a number of players with a maximum of {} players.".format(MAX_PLAYERS) + \
                    "For Example say: Play a game with 3 players."
    return question(speech_output).reprompt(reprompt_text)


@ask.intent('StartGameIntent', mapping={'player_count': 'player_count'})
def start_new_game(player_count):
    # Start a 2d array with rows equal to the number of players. Each column will represent the score of a round.
    player_count = int(player_count)
    player_scores = []
    for i in range(player_count):
        player_scores.append([])
    redis_client.set(REDIS_SET_NAME, json.dumps(player_scores))
    logger.info("Starting session {0} for {1} players".format(REDIS_SET_NAME, player_count))
    return statement("{0} has started a game for {1} players. Player 1 start.".format(REDIS_SET_NAME, player_count))

@ask.intent('GetScoreIntent')
def get_current_score():
    logger.info("Here is the game state")
    game_state = redis_client.get(REDIS_SET_NAME)
    print game_state
    if game_state == None:
        logger.info("Tried to add score to game with session {}, but no such session exists".format(REDIS_SET_NAME))
        return statement("You don't have a game started yet! Please start a game with: Play a game with 2 players")
    player_scores = json.loads(game_state)

    current_statement = ""
    number_of_players = len(player_scores)
    for player_number in range (number_of_players):
        current_statement += "Player {} currently has a score of {}. ".format(player_number+1, sum(player_scores[player_number]))

    return statement(current_statement)



@ask.intent('AddScoreIntent')
def addPlayerScore(score_one, score_two, score_three, player_number):
    game_state = redis_client.get(REDIS_SET_NAME)
    logger.info("Game state thus far:")
    print game_state
    if game_state == None:
        logger.info("Tried to add score to game with session {}, but no such session exists".format(REDIS_SET_NAME))
        return statement("You don't have a game started yet! Please start a game with: Play a game with 2 players")
    score_one = int(score_one)
    score_two = int(score_two)
    score_three = int(score_three)
    player_number = int(player_number)
    player_scores = json.loads(game_state)
    number_of_players = len(player_scores)
    logger.info("processing scores {}, {}, and {} for player {}".format(score_one, score_two, score_three, player_number))

    if number_of_players < player_number or 0 >= player_number:
        logger.info("For session {0}, attempting to add score to player {1}".format(REDIS_SET_NAME, player_number))
        return statement("There are players 1 through {0}, no player with number {1}".format(len(player_scores), player_number))

    player_score = sum(player_scores[player_number-1])
    logger.info("Current score of {} is {}".format(player_number, player_score))
    score_to_add = score_one + score_two + score_three
    logger.info("Adding score {0} to player {1}, who currently has a score of {2}".format(score_to_add, player_number, player_score))

    if player_score + score_to_add > 301:
        logger.info("Player {0} of game {1} busted by adding {2}, to {3}".format(player_number, REDIS_SET_NAME, score_to_add, player_scores))
        player_scores[player_number-1].append(0)
        return statement("BUSTED with a score of {}".format(player_score + score_to_add))

    elif player_score + score_to_add == 301:
        player_scores[player_number - 1].append(score_to_add)
        redis_client.set(REDIS_SET_NAME, json.dumps(player_scores))
        return statement("Player {0} won handily! Congratulations player {0}.".format(player_number))

    next_player = 1
    if player_number != number_of_players:
        next_player = player_number+1

    player_scores[player_number - 1].append(score_to_add)
    redis_client.set(REDIS_SET_NAME, json.dumps(player_scores))
    return statement("Player {} now has a score of {}. Your turn player {}".format(player_number, player_score + score_to_add, next_player))


@ask.session_ended
def session_ended():
    return "", 200


if __name__ == '__main__':
    app.run(debug=True)
