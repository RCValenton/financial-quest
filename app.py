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

@app.route('/investment_decision')
def investment_decision():
    event = player_data.get('investment_event', None)
    if event:
        return render_template('investment.html', player_data=player_data, event=event)
    return redirect(url_for('town'))  # Redirect to town if no investment event exists


@app.route('/work_action', methods=['POST'])
def work_action():
    job = player_data['job']
    
    if job == 'Part-time Job':
        player_data['money'] += 1000
    elif job == 'Online Business':
        player_data['money'] += 2000

    # Decrease health and mental state after working
    player_data['health'] = max(player_data['health'] - 5, 0)
    player_data['mental_state'] = max(player_data['mental_state'] - 5, 0)

    # Check for Game Over
    if player_data['health'] == 0:
        return redirect(url_for('game_over', reason="health"))
    elif player_data['mental_state'] == 0:
        return redirect(url_for('game_over', reason="mental_state"))

    # Check for side hustle outcome
    side_hustle_message = check_side_hustle_outcome()

    # Call random_event() to see if an event occurs and get the event message
    event_message = random_event()

    # Check if it's a side hustle that requires a decision
    if player_data.get('side_hustle') and not player_data['side_hustle']['accepted']:
        return redirect(url_for('side_hustle_decision'))

    # Check if it's an investment event that requires a decision
    if player_data.get('investment_event'):
        return redirect(url_for('investment_decision'))

    return render_template('work.html', player_data=player_data, event_message=side_hustle_message or event_message)


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

# Route for the bank page
@app.route('/bank')
def bank():
    return render_template('bank.html', player_data=player_data)

# Handle taking a loan
@app.route('/take_loan', methods=['POST'])
def take_loan():
    player_data['money'] += 5000
    player_data['debt'] += 5000 * 1.05  # 5% interest
    return redirect(url_for('bank'))

# Handle paying off debt
@app.route('/pay_debt', methods=['POST'])
def pay_debt():
    if player_data['debt'] >= 1000 and player_data['money'] >= 1000:
        player_data['debt'] -= 1000
        player_data['money'] -= 1000
    return redirect(url_for('bank'))

# Handle depositing money into savings
@app.route('/deposit_savings', methods=['POST'])
def deposit_savings():
    deposit_amount = request.form['deposit_amount']

    # Check if deposit_amount is empty or not a valid number
    if not deposit_amount.isdigit() or int(deposit_amount) <= 0:
        # If it's empty or not a valid positive number, redirect back to the bank page with no action
        return redirect(url_for('bank'))
    
    deposit_amount = int(deposit_amount)

    # Check if the player has enough money to deposit
    if player_data['money'] >= deposit_amount:
        player_data['money'] -= deposit_amount
        player_data['savings'] += deposit_amount
    
    return redirect(url_for('bank'))


# Route for food shop
@app.route('/food')
def food():
    return render_template('food.html', player_data=player_data)

# Route to handle buying food
@app.route('/buy_food', methods=['POST'])
def buy_food():
    if player_data['money'] >= 50:  # Ensure the player has enough money
        player_data['money'] -= 50
        player_data['health'] = min(player_data['health'] + 10, 100)  # Cap health at 100

    return redirect(url_for('food'))  # Redirect back to the Food Shop

# Route for entertainment
@app.route('/entertainment')
def entertainment():
    return render_template('entertainment.html', player_data=player_data)

# Route to handle spending on entertainment
@app.route('/buy_entertainment', methods=['POST'])
def buy_entertainment():
    if player_data['money'] >= 200:  # Ensure the player has enough money
        player_data['money'] -= 200
        player_data['mental_state'] = min(player_data['mental_state'] + 20, 100)  # Cap mental state at 100

    return redirect(url_for('entertainment'))  # Redirect back to the Entertainment venue

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
# Expanded random event function to include side hustle discovery
def random_event():
    event_probability = random.random()

    # 15% chance of a random event, splitting between types of events
    if event_probability < 0.15:
        event_type = random.choice(['good', 'bad', 'investment', 'side_hustle'])

        if event_type == 'good':
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
                player_data['mental_state'] = min(player_data['mental_state'] + 20, 100)

        elif event_type == 'bad':
            event = random.choice([
                "You had a medical emergency, costing $1000 in bills!",
                "You lost your wallet, $300 gone!",
                "You had a stressful week, mental state -20!"
            ])
            if "medical emergency" in event:
                player_data['money'] -= 1000
                player_data['health'] = max(player_data['health'] - 10, 0)
            elif "lost your wallet" in event:
                player_data['money'] -= 300
            elif "stressful week" in event:
                player_data['mental_state'] = max(player_data['mental_state'] - 20, 0)

        elif event_type == 'investment':
            event = random.choice([
                "A friend suggests you invest $1000 in a new business venture. Do you accept?",
                "You find out about a stock opportunity. Invest $2000 for a chance to double your money!"
            ])
            player_data['investment_event'] = event
            return None  # Return None to indicate the event requires input

        elif event_type == 'side_hustle':
            side_hustles = ['selling homemade candles', 'starting a blog', 'creating an online store', 'becoming a freelancer']
            side_hustle_name = random.choice(side_hustles)
            event = f"You discovered a side hustle opportunity: {side_hustle_name}. Do you want to accept?"

            player_data['side_hustle'] = {
                'name': side_hustle_name,
                'days_until_outcome': random.randint(1, 3),
                'accepted': False
            }
            return None

        return event
    return None




def check_side_hustle_outcome():
    side_hustle = player_data.get('side_hustle', None)

    if side_hustle and side_hustle['accepted']:
        side_hustle['days_until_outcome'] -= 1

        if side_hustle['days_until_outcome'] <= 0:
            if random.random() < 0.5:  # 50% chance for success
                player_data['money'] += 1000
                event_message = f"Your side hustle '{side_hustle['name']}' was a success! You earned $1000."
            else:
                player_data['money'] -= 500
                event_message = f"Your side hustle '{side_hustle['name']}' failed, and you had to pay $500 in production costs."

            # Clear the side hustle after it's resolved
            player_data['side_hustle'] = None

            return event_message
    return None


@app.route('/side_hustle_decision')
def side_hustle_decision():
    side_hustle = player_data.get('side_hustle', None)
    if side_hustle and not side_hustle['accepted']:
        return render_template('side_hustle.html', player_data=player_data, side_hustle=side_hustle)
    return redirect(url_for('town'))  # Redirect to town if no side hustle is pending

@app.route('/handle_side_hustle', methods=['POST'])
def handle_side_hustle():
    decision = request.form['decision']
    side_hustle = player_data.get('side_hustle', None)

    if side_hustle:
        if decision == 'accept':
            player_data['side_hustle']['accepted'] = True
            event_message = f"You accepted the side hustle: {side_hustle['name']}. The outcome will be decided in {side_hustle['days_until_outcome']} days."
        else:
            player_data['side_hustle'] = None  # Reject the side hustle
            event_message = "You decided not to pursue the side hustle."

        return render_template('town.html', player_data=player_data, event_message=event_message)
    
    return redirect(url_for('town'))

@app.route('/handle_investment', methods=['POST'])
def handle_investment():
    decision = request.form['decision']
    event = player_data.get('investment_event', None)
    
    if event:
        if decision == 'accept':
            # Investment decision was accepted
            if "Invest $1000" in event:
                if random.random() < 0.5:  # 50% chance to succeed
                    player_data['money'] += 1000
                    event_message = "The investment paid off! You earned $1000."
                else:
                    player_data['money'] -= 1000
                    event_message = "The investment failed. You lost $1000."
            elif "Invest $2000" in event:
                if random.random() < 0.5:
                    player_data['money'] += 2000
                    event_message = "The stock soared! You earned $2000."
                else:
                    player_data['money'] -= 2000
                    event_message = "The stock crashed. You lost $2000."
        else:
            # Investment decision was declined
            event_message = "You decided not to invest."

        # Clear the investment event after processing
        player_data['investment_event'] = None

        # Redirect to the town or any other relevant page after investment
        return render_template('town.html', player_data=player_data, event_message=event_message)
    
    return redirect(url_for('town'))


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

    # Check for Game Over
    if player_data['health'] == 0:
        return redirect(url_for('game_over', reason="health"))
    elif player_data['mental_state'] == 0:
        return redirect(url_for('game_over', reason="mental_state"))

    # Check for random event
    event_message = random_event()

    # Check for victory condition
    if player_data['debt'] == 0 and player_data['money'] >= 1000000:
        return redirect(url_for('victory'))

    # Redirect the player back to the game page after making a decision
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
