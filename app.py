from flask import Flask, render_template, request, redirect, url_for

# Initialize the Flask app
app = Flask(__name__)

# Initial data for the player
player_data = {
    'money': 2000,  # Starting with $2000 in the bank
    'job': None,
    'savings': 0,
    'debt': 100000,  # Starting debt of $100,000
    'investments': 0,
    'health': 100,  # Initial health value
    'mental_state': 100,  # Initial mental state value
    'day': 1  # Start at day 1
}

def reset_game():
    global player_data
    player_data = {
        'money': 2000,  # Starting with $2000 in the bank
        'job': None,
        'savings': 0,
        'debt': 100000,  # Starting debt of $100,000
        'investments': 0,
        'health': 100,  # Initial health value
        'mental_state': 100,  # Initial mental state value
        'day': 1  # Start at day 1
    }

# Route for the lore introduction
@app.route('/')
def lore():
    print("Lore page loaded")
    return render_template('lore.html', player_data=player_data)

# Route to handle job selection after lore
@app.route('/choose_job', methods=['POST'])
def choose_job():
    selected_job = request.form['job']
    if selected_job == 'part_time':
        player_data['job'] = 'Part-time Job'
        player_data['money'] += 1000  # Initial income from part-time job
    elif selected_job == 'business':
        player_data['job'] = 'Online Business'
        player_data['money'] += 2000  # Initial income from starting a business

    return redirect(url_for('game'))

# Route for the main game page
@app.route('/game')
def game():
    return render_template('game.html', player_data=player_data)

# Route to handle financial decisions
@app.route('/decision', methods=['POST'])
def decision():
    decision = request.form['decision']
    
    # Update the day counter
    player_data['day'] += 1

    # Handle financial decisions
    if decision == 'save':
        player_data['savings'] += player_data['money'] * 0.1
        player_data['money'] -= player_data['money'] * 0.1
    elif decision == 'invest':
        player_data['investments'] += player_data['money'] * 0.2
        player_data['money'] -= player_data['money'] * 0.2
    elif decision == 'spend':
        player_data['money'] -= 500  # Spend $500 on lifestyle
        player_data['mental_state'] += 10  # Increase mental state
    elif decision == 'pay_debt':
        if player_data['debt'] >= 1000:
            player_data['debt'] -= 1000  # Pay off $1000 in debt
            player_data['money'] -= 1000
        else:
            player_data['money'] -= player_data['debt']
            player_data['debt'] = 0  # Debt fully paid
    elif decision == 'take_loan':
        player_data['money'] += 5000  # Add loan to money
        player_data['debt'] += 5000 * 1.05  # 5% interest on loan
    elif decision == 'side_hustle':
        player_data['money'] += 3000  # Earn $3000 from side hustle
    elif decision == 'buy_food':
        player_data['money'] -= 50  # Buy food for $50
        player_data['health'] += 10  # Increase health by 10
    elif decision == 'buy_entertainment':
        player_data['money'] -= 200  # Spend on entertainment
        player_data['mental_state'] += 20  # Increase mental state

    # Decrease health and mental state every day
    player_data['health'] -= 5
    player_data['mental_state'] -= 5

    # Game over conditions
    if player_data['mental_state'] <= 0:
        return redirect(url_for('game_over', reason="mental_state"))
    elif player_data['health'] <= 0:
        return redirect(url_for('game_over', reason="health"))

    return redirect(url_for('game'))

# Game over screen
@app.route('/game_over/<reason>')
def game_over(reason):
    if reason == "mental_state":
        message = "Game Over! You've given up and ended up homeless due to poor mental health."
    elif reason == "health":
        message = "Game Over! You've succumbed to illness due to poor health."
    
    return render_template('game_over.html', message=message)

# Route to handle restarting the game
@app.route('/restart_game')
def restart_game():
    reset_game()  # Reset the player data
    return redirect(url_for('lore'))  # Redirect to the lore page to restart



# Running the app
if __name__ == '__main__':
    app.run(debug=True)
