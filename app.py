
import random
import string
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

app = Flask(__name__)
app.secret_key = 'rockpaperscissors_secret_key'

# In-memory game storage
games = {}

def generate_game_id(length=6):
	return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def determine_winner(choice1, choice2):
	if choice1 == choice2:
		return 'tie'
	elif (
		(choice1 == 'rock' and choice2 == 'scissors') or
		(choice1 == 'scissors' and choice2 == 'paper') or
		(choice1 == 'paper' and choice2 == 'rock')
	):
		return 'p1'
	else:
		return 'p2'

@app.route('/', methods=['GET', 'POST'])
def home():
	return render_template('home.html')

@app.route('/create_game', methods=['POST'])
def create_game():
	game_id = generate_game_id()
	games[game_id] = {
		'players': {},
		'rounds': [],
		'max_rounds': 5,
		'state': 'waiting',
		'winner': None
	}
	return redirect(url_for('join_game', game_id=game_id, player='p1'))

@app.route('/game/<game_id>/join/<player>', methods=['GET', 'POST'])
def join_game(game_id, player):
	if game_id not in games or player not in ['p1', 'p2']:
		return "Invalid game.", 404
	if request.method == 'POST':
		name = request.form.get('player_name', '').strip()
		if not name:
			return render_template('join.html')
		games[game_id]['players'][player] = name
		# If both players joined, set state to playing
		if len(games[game_id]['players']) == 2:
			games[game_id]['state'] = 'playing'
		session['game_id'] = game_id
		session['player'] = player
		return redirect(url_for('play_game', game_id=game_id))
	return render_template('join.html')

@app.route('/game/<game_id>/play', methods=['GET', 'POST'])
def play_game(game_id):
	if 'game_id' not in session or 'player' not in session or session['game_id'] != game_id:
		return redirect(url_for('join_game', game_id=game_id, player='p1'))
	game = games.get(game_id)
	player = session['player']
	opponent = 'p2' if player == 'p1' else 'p1'
	if request.method == 'POST' and game['state'] == 'playing':
		choice = request.form.get('choice')
		if 'choices' not in game:
			game['choices'] = {}
		if player not in game['choices']:
			game['choices'][player] = choice
		# If both players have chosen, resolve round
		if len(game['choices']) == 2:
			p1_choice = game['choices'].get('p1')
			p2_choice = game['choices'].get('p2')
			winner = determine_winner(p1_choice, p2_choice)
			round_result = {
				'round': len(game['rounds']) + 1,
				'p1_choice': p1_choice,
				'p2_choice': p2_choice,
				'result': winner
			}
			game['rounds'].append(round_result)
			game.pop('choices')
			# Score
			p1_score = sum(1 for r in game['rounds'] if r['result'] == 'p1')
			p2_score = sum(1 for r in game['rounds'] if r['result'] == 'p2')
			# End game if needed
			if p1_score == 3 or p2_score == 3 or len(game['rounds']) == game['max_rounds']:
				game['state'] = 'gameover'
				if p1_score > p2_score:
					game['winner'] = 'p1'
				elif p2_score > p1_score:
					game['winner'] = 'p2'
				else:
					game['winner'] = 'tie'
	# Prepare context
	p1_name = game['players'].get('p1', 'Player 1')
	p2_name = game['players'].get('p2', 'Player 2')
	p1_score = sum(1 for r in game['rounds'] if r['result'] == 'p1')
	p2_score = sum(1 for r in game['rounds'] if r['result'] == 'p2')
	round_num = len(game['rounds']) + (1 if game.get('choices') else 0)
	max_rounds = game['max_rounds']
	history = game['rounds']
	waiting = game['state'] == 'playing' and (not game.get('choices') or player not in game.get('choices', {}))
	chosen = game.get('choices', {}).get(player) is not None if game.get('choices') else False
	gameover = game['state'] == 'gameover'
	winner = game.get('winner')
	winner_name = p1_name if winner == 'p1' else (p2_name if winner == 'p2' else 'Tie')
	return render_template('play.html',
		player1_name=p1_name,
		player2_name=p2_name,
		player1_score=p1_score,
		player2_score=p2_score,
		round_num=round_num,
		max_rounds=max_rounds,
		history=history,
		waiting=waiting,
		chosen=chosen,
		gameover=gameover,
		winner=winner,
		winner_name=winner_name,
		game_id=game_id
	)

@app.route('/game/<game_id>/status')
def game_status(game_id):
	game = games.get(game_id)
	if not game:
		return jsonify({'reload': True})
	# If both players have chosen, signal reload
	reload = False
	if game.get('choices') and len(game['choices']) == 2:
		reload = True
	if game['state'] == 'gameover':
		reload = True
	return jsonify({'reload': reload})

@app.route('/game/<game_id>/choice', methods=['POST'])
def make_choice(game_id):
	# This route is not used in this implementation, but could be used for AJAX
	return '', 204

@app.route('/game/<game_id>/reset', methods=['POST'])
def reset_game(game_id):
	game = games.get(game_id)
	if not game:
		return redirect(url_for('home'))
	game['rounds'] = []
	game['state'] = 'playing'
	game['winner'] = None
	return redirect(url_for('play_game', game_id=game_id))

if __name__ == "__main__":
	app.run(host='0.0.0.0', port=5000, debug=True)