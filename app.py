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
    
    if decision == 'save':
        player_data['savings'] += player_data['money'] * 0.1
        player_data['money'] -= player_data['money'] * 0.1
    elif decision == 'invest':
        player_data['investments'] += player_data['money'] * 0.2
        player_data['money'] -= player_data['money'] * 0.2
    elif decision == 'spend':
        player_data['money'] -= 500  # Spend $500
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

    return redirect(url_for('game'))


# Running the app
if __name__ == '__main__':
    app.run(debug=True)
