from flask import Flask, render_template, request, redirect, url_for

# Initialize the Flask app
app = Flask(__name__)

# Initial data for the player
player_data = {
    'money': 2000,
    'job': None,
    'savings': 0,
    'debt': 100000,
    'investments': 0,
    'health': 100,
    'mental_state': 100,
    'day': 1,
    'time': 6,  # Start at 6 AM
    'period': 'AM',  # Start with AM
}

# Function to reset the game data
def reset_game():
    global player_data
    player_data = {
        'money': 2000,
        'job': None,
        'savings': 0,
        'debt': 100000,
        'investments': 0,
        'health': 100,
        'mental_state': 100,
        'day': 1,
        'time': 6,  # Start at 6 AM
        'period': 'AM',
    }

# Function to update time and toggle AM/PM
def update_time():
    player_data['time'] += 1
    if player_data['time'] == 12:
        if player_data['period'] == 'AM':
            player_data['period'] = 'PM'
        else:
            player_data['period'] = 'AM'
            player_data['day'] += 1  # Increment day when it turns from PM to AM
    elif player_data['time'] == 13:
        player_data['time'] = 1  # Reset time after 12-hour format

@app.route('/')
def lore():
    return render_template('lore.html', player_data=player_data)

@app.route('/choose_job', methods=['POST'])
def choose_job():
    selected_job = request.form['job']
    if selected_job == 'part_time':
        player_data['job'] = 'Part-time Job'
        player_data['money'] += 1000
    elif selected_job == 'business':
        player_data['job'] = 'Online Business'
        player_data['money'] += 2000

    return redirect(url_for('game'))

@app.route('/game')
def game():
    return render_template('game.html', player_data=player_data)

@app.route('/decision', methods=['POST'])
def decision():
    decision = request.form['decision']
    
    # Update the time (for each decision, the time advances)
    update_time()

    # Financial and health decisions
    if decision == 'save':
        player_data['savings'] += player_data['money'] * 0.1
        player_data['money'] -= player_data['money'] * 0.1
    elif decision == 'invest':
        player_data['investments'] += player_data['money'] * 0.2
        player_data['money'] -= player_data['money'] * 0.2
    elif decision == 'spend':
        player_data['money'] -= 500
        player_data['mental_state'] += 10
    elif decision == 'pay_debt':
        if player_data['debt'] >= 1000:
            player_data['debt'] -= 1000
            player_data['money'] -= 1000
        else:
            player_data['money'] -= player_data['debt']
            player_data['debt'] = 0
    elif decision == 'take_loan':
        player_data['money'] += 5000
        player_data['debt'] += 5000 * 1.05
    elif decision == 'side_hustle':
        player_data['money'] += 3000
    elif decision == 'buy_food':
        player_data['money'] -= 50
        player_data['health'] += 10
    elif decision == 'buy_entertainment':
        player_data['money'] -= 200
        player_data['mental_state'] += 20

    # Health and mental state degrade every cycle
    player_data['health'] -= 5
    player_data['mental_state'] -= 5

    # Check for game over conditions
    if player_data['mental_state'] <= 0:
        return redirect(url_for('game_over', reason="mental_state"))
    elif player_data['health'] <= 0:
        return redirect(url_for('game_over', reason="health"))

    return redirect(url_for('game'))

@app.route('/game_over/<reason>')
def game_over(reason):
    if reason == "mental_state":
        message = "Game Over! You've given up and ended up homeless due to poor mental health."
    elif reason == "health":
        message = "Game Over! You've succumbed to illness due to poor health."
    
    return render_template('game_over.html', message=message)

@app.route('/restart_game')
def restart_game():
    reset_game()
    return redirect(url_for('lore'))


# Running the app
if __name__ == '__main__':
    app.run(debug=True)
