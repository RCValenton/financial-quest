import matplotlib.pyplot as plt
import os
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

# Fake stock market data
categories = {
    "Technology": ["TechCo", "InnoSoft", "MicroWeb", "CloudGen", "DataFlow", "QuantumAI", "GreenEnergy", "SmartSys", "NetCom", "CyberTech"],
    "Healthcare": ["MediLife", "PharmaPlus", "BioHealth", "WellnessCorp", "GeneNext", "CarePlan", "VaccineX", "TheraMed", "GlobalHealth", "MedSolutions"],
    "Energy": ["EcoFuel", "SunPower", "GreenOil", "EnergyWave", "WindForce", "BioGasCo", "SolarMax", "PowerFusion", "HydroEnergy", "EarthPower"],
    "Finance": ["SafeBank", "WealthyTrust", "CapitalGroup", "InvestCo", "LoanSecure", "GlobalInvest", "MoneyStream", "CashHold", "FundMate", "EquityPlus"],
    "Consumer Goods": ["FreshFood", "DrinkLife", "SafeHome", "DailyGoods", "CleanCorp", "HomeEssentials", "QuickSnacks", "StyleBrand", "LuxCloth", "HappyHome"]
}

starting_prices = {
    "Technology": 150, "Healthcare": 100, "Energy": 50, "Finance": 80, "Consumer Goods": 60
}

volatility_factors = {
    "Technology": 0.02, "Healthcare": 0.015, "Energy": 0.03, "Finance": 0.01, "Consumer Goods": 0.012
}

# Initialize stocks with starting prices
stock_market = {}
for category, stocks in categories.items():
    stock_market[category] = {stock: starting_prices[category] for stock in stocks}

# Simulate stock price updates
def update_stock_price(category, price):
    sector_trend = random.uniform(-0.02, 0.02)  # Simulate sector-wide trends
    random_fluctuation = random.uniform(-volatility_factors[category], volatility_factors[category])
    price_change = price * (sector_trend + random_fluctuation)
    return round(price + price_change, 2)

# Simulate one day of stock price updates
def simulate_stock_market():
    for category, stocks in stock_market.items():
        for stock, price in stocks.items():
            new_price = update_stock_price(category, price)
            stock_market[category][stock] = new_price

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

# Function to check and trigger storyline milestones
def check_storyline():
    storyline_message = None
    
    if player_data['debt'] <= 75000 and player_data['debt'] > 50000:
        storyline_message = "You're making great progress in paying off your debt! Keep going!"
    elif player_data['debt'] <= 50000 and player_data['debt'] > 0:
        storyline_message = "You're halfway to paying off your debt! Stay focused and healthy."
    elif player_data['debt'] == 0 and player_data['money'] < 1000000:
        storyline_message = "Congratulations on paying off your debt! Now it's time to focus on building your wealth."
    elif player_data['money'] >= 1000000:
        storyline_message = "You've reached your goal of $1,000,000! You've achieved financial freedom!"
    
    return storyline_message

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

# Add this function to generate a stock price graph
def generate_stock_chart():
    # Simulate stock price history (for simplicity, generating random historical prices)
    stock_history = {
        "TechCo": [random.uniform(50, 150) for _ in range(10)],
        "MediLife": [random.uniform(20, 80) for _ in range(10)],
        "EcoFuel": [random.uniform(30, 90) for _ in range(10)]
    }

    plt.figure(figsize=(10, 6))

    # Plot each stock's price history
    for stock_name, prices in stock_history.items():
        plt.plot(prices, label=stock_name)

    plt.title("Stock Prices Over Time")
    plt.xlabel("Time (days)")
    plt.ylabel("Price")
    plt.legend()

    # Save the graph as an image in the static folder
    if not os.path.exists('static/images'):
        os.makedirs('static/images')
    plt.savefig('static/images/stock_chart.png')
    plt.close()


# Call this function when rendering the investment center page
@app.route('/investment_center')
def investment_center():
    simulate_stock_market()  # Simulate stock updates before rendering
    generate_stock_chart()   # Generate the stock price chart
    return render_template('stock_market.html', stock_market=stock_market, player_data=player_data)

@app.route('/buy_stock', methods=['POST'])
def buy_stock():
    stock_name = request.form['stock_name']
    
    # Find the stock and buy it
    for category, stocks in stock_market.items():
        if stock_name in stocks:
            stock_price = stocks[stock_name]
            if player_data['money'] >= stock_price:  # Ensure player has enough money
                player_data['money'] -= stock_price
                player_data['investments'] += stock_price  # Add stock value to investments
                return redirect(url_for('investment_center'))

    return redirect(url_for('investment_center'))

@app.route('/sell_stock', methods=['POST'])
def sell_stock():
    stock_name = request.form['stock_name']
    
    # Find the stock and sell it
    for category, stocks in stock_market.items():
        if stock_name in stocks:
            stock_price = stocks[stock_name]
            player_data['money'] += stock_price  # Add money from selling the stock
            player_data['investments'] -= stock_price  # Deduct from investments
            return redirect(url_for('investment_center'))

    return redirect(url_for('investment_center'))

# Decrease health and mental state after working
def reduce_health_mental_state():
    player_data['health'] = max(player_data['health'] - 5, 0)
    player_data['mental_state'] = max(player_data['mental_state'] - 5, 0)

# Check for Game Over
def check_game_over():
    if player_data['health'] == 0:
        return redirect(url_for('game_over', reason="health"))
    elif player_data['mental_state'] == 0:
        return redirect(url_for('game_over', reason="mental_state"))
    return None

# Route for handling work actions
@app.route('/work_action', methods=['POST'])
def work_action():
    job = player_data['job']
    
    if job == 'Part-time Job':
        player_data['money'] += 1000
    elif job == 'Online Business':
        player_data['money'] += 2000

    # Decrease health and mental state after working
    reduce_health_mental_state()

    # Check for Game Over
    game_over_redirect = check_game_over()
    if game_over_redirect:
        return game_over_redirect

    # Check for storyline progression
    storyline_message = check_storyline()

    # Call random_event() to see if an event occurs and get the event message
    event_message = random_event()

    return render_template('work.html', player_data=player_data, storyline_message=storyline_message, event_message=event_message)

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

# Function to simulate stock price changes
def update_stock_prices():
    for stock in stocks:
        # High-risk stocks fluctuate more than low-risk stocks
        if stock['risk'] == 'high':
            stock['price'] += random.uniform(-20, 20)
        elif stock['risk'] == 'medium':
            stock['price'] += random.uniform(-10, 10)
        else:
            stock['price'] += random.uniform(-5, 5)
        
        # Ensure stock price doesn’t go below 1
        stock['price'] = max(stock['price'], 1)

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

