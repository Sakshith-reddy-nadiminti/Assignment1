#!/usr/bin/env python3
"""Web frontend for Tic-Tac-Toe game with Minimax AI."""

from flask import Flask, jsonify, render_template
from flask_cors import CORS
from tic_tac_toe import Board, Player, Game

app = Flask(__name__)
CORS(app)

# Game instance shared across requests
game = None

def get_game():
    global game
    if game is None or game.game_over:
        game = Game(ai_player=Player.O)
    return game

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/board', methods=['GET'])
def get_board():
    g = get_game()
    cells = [[g.board._cells[r][c].value for c in range(3)] for r in range(3)]
    return jsonify({
        'board': cells,
        'current_player': g.current_player.value,
        'game_over': g.game_over,
        'winner': g.winner.value if g.winner else None,
        'status': g.get_status()
    })

@app.route('/api/move', methods=['POST'])
def make_move():
    from flask import request
    data = request.get_json()
    row = data.get('row', 0)
    col = data.get('col', 0)

    g = get_game()
    success = g.play_human_move(row, col)

    cells = [[g.board._cells[r][c].value for c in range(3)] for r in range(3)]
    return jsonify({
        'success': success,
        'board': cells,
        'current_player': g.current_player.value,
        'game_over': g.game_over,
        'winner': g.winner.value if g.winner else None,
        'status': g.get_status()
    })

@app.route('/api/reset', methods=['POST'])
def reset():
    global game
    game = Game(ai_player=Player.O)
    return jsonify({'message': 'Game reset'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)