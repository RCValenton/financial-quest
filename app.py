import random
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
        'time': 6,
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

# Route for apartment page (starting point after selecting a job)
@app.route('/apartment')
def apartment():
    return render_template('apartment.html', player_data=player_data)

@app.route('/town')
def town():
    return render_template('town.html', player_data=player_data)

# Route for work page
@app.route('/work')
def work():
    if player_data['job']:  # If the player already has a job
        return render_template('work.html', player_data=player_data)
    else:
        return render_template('choose_job.html')

# Handle job selection from the work page
@app.route('/choose_job', methods=['POST'])
def choose_job():
    selected_job = request.form['job']
    if selected_job == 'part_time':
        player_data['job'] = 'Part-time Job'
        player_data['money'] += 1000
    elif selected_job == 'business':
        player_data['job'] = 'Online Business'
        player_data['money'] += 2000

    # Redirect the player to the apartment page after selecting a job
    return redirect(url_for('apartment'))


# Example route for bank (expand on this)
@app.route('/bank')
def bank():
    return "<h1>Welcome to the Bank</h1><p>Bank functionality will be implemented soon.</p><a href='/town'>Go Back to Town</a>"

# Example route for food shop (expand on this)
@app.route('/food')
def food():
    return "<h1>Welcome to the Food Shop</h1><p>Buy food here to maintain your health!</p><a href='/town'>Go Back to Town</a>"

# Example route for entertainment (expand on this)
@app.route('/entertainment')
def entertainment():
    return "<h1>Welcome to the Entertainment Venue</h1><p>Spend some money to improve your mental state!</p><a href='/town'>Go Back to Town</a>"

# Route for restarting the game
@app.route('/restart_game')
def restart_game():
    reset_game()
    return redirect(url_for('apartment'))

# Route for the main lore page
@app.route('/')
def lore():
    return render_template('lore.html', player_data=player_data)

# Function to handle random events
def random_event():
    event_probability = random.random()

    # Example events with 10% chance of occurring each time
    if event_probability < 0.10:
        event_type = random.choice(['good', 'bad'])

        if event_type == 'good':
            # Good event: bonus money or mental boost
            event = random.choice([
                "You found $500 on the street!",
                "Your side hustle paid off unexpectedly well, you earned $1000!",
                "You had an amazing time with friends, mental state +20!"
            ])

            if "found $500" in event:
                player_data['money'] += 500
            elif "side hustle" in event:
                player_data['money'] += 1000
            elif "amazing time" in event:
                player_data['mental_state'] += 20
        
        elif event_type == 'bad':
            # Bad event: money loss or health reduction
            event = random.choice([
                "You had a medical emergency, costing $1000 in bills!",
                "You lost your wallet, $300 gone!",
                "You had a stressful week, mental state -20!"
            ])

            if "medical emergency" in event:
                player_data['money'] -= 1000
                player_data['health'] -= 10
            elif "lost your wallet" in event:
                player_data['money'] -= 300
            elif "stressful week" in event:
                player_data['mental_state'] -= 20

        return event  # Return the event message to display to the player
    
    return None  # No event occurred

# Route for making decisions
@app.route('/decision', methods=['POST'])
def decision():
    decision = request.form['decision']
    
    # Update the time (for each decision, the time advances)
    update_time()

    # Health and mental state degrade every cycle first
    player_data['health'] = max(player_data['health'] - 5, 0)  # Health shouldn't go below 0
    player_data['mental_state'] = max(player_data['mental_state'] - 5, 0)  # Mental state shouldn't go below 0

    # Financial and health decisions
    if decision == 'save':
        player_data['savings'] += round(player_data['money'] * 0.1, 2)  # Round to 2 decimal places
        player_data['money'] -= round(player_data['money'] * 0.1, 2)
    elif decision == 'invest':
        player_data['investments'] += round(player_data['money'] * 0.2, 2)
        player_data['money'] -= round(player_data['money'] * 0.2, 2)
    elif decision == 'spend':
        player_data['money'] -= 500
        player_data['mental_state'] = min(player_data['mental_state'] + 10, 100)  # Cap mental state at 100
    elif decision == 'pay_debt':
        if player_data['debt'] >= 1000:
            player_data['debt'] -= round(1000, 2)
            player_data['money'] -= round(1000, 2)
        else:
            player_data['money'] -= round(player_data['debt'], 2)
            player_data['debt'] = 0
    elif decision == 'take_loan':
        player_data['money'] += round(5000, 2)
        player_data['debt'] += round(5000 * 1.05, 2)  # 5% interest
    elif decision == 'side_hustle':
        player_data['money'] += round(3000, 2)
    elif decision == 'buy_food':
        player_data['money'] -= round(50, 2)
        player_data['health'] = min(player_data['health'] + 10, 100)  # Cap health at 100
    elif decision == 'buy_entertainment':
        player_data['money'] -= round(200, 2)
        player_data['mental_state'] = min(player_data['mental_state'] + 20, 100)  # Cap mental state at 100

    # Format money and debt to 2 decimal places
    player_data['money'] = round(player_data['money'], 2)
    player_data['debt'] = round(player_data['debt'], 2)

    # Check for random event
    event_message = random_event()

    # Check for victory condition
    if player_data['debt'] == 0 and player_data['money'] >= 1000000:
        return redirect(url_for('victory'))

    # Check for game over conditions
    if player_data['mental_state'] <= 0:
        return redirect(url_for('game_over', reason="mental_state"))
    elif player_data['health'] <= 0:
        return redirect(url_for('game_over', reason="health"))

    return render_template('game.html', player_data=player_data, event_message=event_message)

# Route for victory screen
@app.route('/victory')
def victory():
    return render_template('victory.html')

# Route for game over screen
@app.route('/game_over/<reason>')
def game_over(reason):
    if reason == "mental_state":
        message = "Game Over! You've given up and ended up homeless due to poor mental health."
    elif reason == "health":
        message = "Game Over! You've succumbed to illness due to poor health."
    
    return render_template('game_over.html', message=message)

# Running the app
if __name__ == '__main__':
    app.run(debug=True)
