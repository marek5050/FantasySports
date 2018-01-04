from flask import Flask, jsonify, request
from flask.ext.cors import CORS

app = Flask(__name__)
CORS(app)

# import degenerate
from degenerate.player_pool import PlayerPool
from degenerate.optimizer import Optimizer
from degenerate.roster_definition import RosterDefinition

NUMBER_OF_LINEUPS = 3
UNIQUE_PLAYERS = 8

player_pool = PlayerPool().from_csv('./projections/sample-nba.csv')
optimizer = Optimizer()

roster_definition = RosterDefinition.DK_CFB


@app.route("/player-pool")
def get_player_pool():
    return jsonify({"players": player_pool.as_json()})


@app.route("/optimize", methods=['POST'])
def post_optimize():
    content = request.get_json()
    pool = PlayerPool().from_json(content)

    rosters = []
    for i in range(0, 3):
        rosters.append(optimizer.generate_roster(pool.all_players(), \
                                                 roster_definition, \
                                                 rosters, UNIQUE_PLAYERS))

    return jsonify({"rosters": [x.__json__() for x in rosters]})


if __name__ == "__main__":
    # app.debug = True
    app.run()
