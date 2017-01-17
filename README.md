# alexa-301
The search for a method to play 301 without a blackboard

## Prerequisites
This project runs on [flask-ask](https://github.com/johnwheeler/flask-ask) and is deployed via [Zappa](https://github.com/Miserlou/Zappa).
Instructions to deploy projects can be found there, but here's the gist:

* `pip install -r requirements.txt`
* `zappa init`
* `zappa deploy`

## Using The Skill
To start a game, say: 
> Alexa, ask <APP_NAME> to start a game with <player_count> players.

To add a score:
> Alexa, ask <APP_NAME> to give <score_one> then <score_two> then <score_three> to player <player_number>.

To get the current score:
> Alexa, ask <APP_NAME> what the current score is.

## Write Up:
This is the first in a few implementations to let me be lazier while plaing darts. Write up of this first implementation coming soon™.