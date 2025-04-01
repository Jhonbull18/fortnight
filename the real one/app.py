from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # For session management and flash messages


# Database initialization
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute(''' 
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT,
            last_name TEXT,
            address TEXT,
            phone_number TEXT,
            email TEXT UNIQUE,
            password TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Home page
@app.route('/')
def home():
    return render_template('home.html')


# Register page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        address = request.form['address']
        phone_number = request.form['phone_number']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash("Passwords do not match. Please try again.", "danger")
            return redirect(url_for('register'))

        # Hash the password before storing it
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Check if email already exists
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE email = ?', (email,))
        existing_user = c.fetchone()
        conn.close()

        if existing_user:
            flash("Email already registered. Please log in.", "warning")
            return redirect(url_for('login'))

        # Save user data to database
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute(''' 
            INSERT INTO users (first_name, last_name, address, phone_number, email, password) 
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (first_name, last_name, address, phone_number, email, hashed_password))
        conn.commit()
        conn.close()

        flash("Registration successful. Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')


# Profile page
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        flash("You need to log in first.", "warning")
        return redirect(url_for('login'))

    # Fetch user details from the database
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],))
    user = c.fetchone()
    conn.close()

    if request.method == 'POST':
        # Update user details
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        address = request.form['address']
        phone_number = request.form['phone_number']

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('''
            UPDATE users 
            SET first_name = ?, last_name = ?, address = ?, phone_number = ? 
            WHERE id = ?
        ''', (first_name, last_name, address, phone_number, session['user_id']))
        conn.commit()
        conn.close()

        flash("Profile updated successfully.", "success")
        return redirect(url_for('profile'))

    return render_template('profile.html', user=user)




# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Check if the user exists
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = c.fetchone()
        conn.close()

        if user:
            # If user exists, check password
            if check_password_hash(user[6], password):  # user[6] is the hashed password
                session['user_id'] = user[0]  # Store user ID in session
                flash("Login successful!", "success")
                return redirect(url_for('dashboard'))
            else:
                flash("Invalid password. Please try again.", "danger")
                return redirect(url_for('login'))
        else:
            flash("Account does not exist. Please register.", "danger")
            return redirect(url_for('register'))

    return render_template('login.html')



# Dashboard page (Logged-in page)
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash("You need to log in first.", "warning")
        return redirect(url_for('login'))
    return render_template('dashboard.html')


# Logout route
@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Clear session
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))


# Carbon Footprint page
@app.route('/carbon_footprint', methods=['GET', 'POST'])
def carbon_footprint():
    if 'user_id' not in session:
        flash("You need to log in first.", "warning")
        return redirect(url_for('login'))

    if request.method == 'POST':
        energy_source = request.form['energy_source']
        energy_consumed = float(request.form['energy_consumed'])
        carbon_emission_factor = float(request.form['carbon_emission_factor'])
        usage_period = request.form['usage_period']

        # Calculate the carbon footprint (kg CO2)
        carbon_footprint = energy_consumed * carbon_emission_factor

        # Adjust the carbon footprint based on the usage period
        if usage_period == 'daily':
            carbon_footprint_daily = carbon_footprint
            carbon_footprint_monthly = carbon_footprint * 30  # Assuming 30 days in a month
            carbon_footprint_yearly = carbon_footprint * 365  # Assuming 365 days in a year
        elif usage_period == 'monthly':
            carbon_footprint_daily = carbon_footprint / 30
            carbon_footprint_monthly = carbon_footprint
            carbon_footprint_yearly = carbon_footprint * 12
        else:  # yearly
            carbon_footprint_daily = carbon_footprint / 365
            carbon_footprint_monthly = carbon_footprint / 12
            carbon_footprint_yearly = carbon_footprint

        # Flash success message with the result
        flash(f"Your carbon footprint for the selected period is: <br>"
              f"Daily: {carbon_footprint_daily:.2f} kg CO2<br>"
              f"Monthly: {carbon_footprint_monthly:.2f} kg CO2<br>"
              f"Yearly: {carbon_footprint_yearly:.2f} kg CO2", "success")

        return redirect(url_for('carbon_footprint'))

    return render_template('carbon_footprint.html')





# Energy Usage page
@app.route('/energy_usage')
def energy_usage():
    return render_template('energy_usage.html')



@app.route('/credit_card_consultation/<product_id>', methods=['GET', 'POST'])
def credit_card_product(product_id):
    # Example product data (normally fetched from a database)
    products = {
        '1': {'name': ' Solar Panel', 'price': 299.99},
        '2': {'name': 'Electric Vehicle Charger', 'price': 149.99},
        '3': {'name': 'Energy-efficient Appliances', 'price': 89.99},
        '4': {'name': 'Solar Water Heater', 'price': 499.99},
        '5': {'name': 'Smart Thermostat', 'price': 149.00},
        '6': {'name': 'Home Wind Turbine', 'price': 899.99},
        '7': {'name': 'LED Lights', 'price': 29.99},
        '8': {'name': 'Solar Battery', 'price': 399.99},
        '9': {'name': 'Smart Plug', 'price': 19.99},
        '10': {'name': 'Smart Light Bulb', 'price': 15.99},
        '11': {'name': 'Portable Solar Panel', 'price': 249.99},
        '12': {'name': 'Electric Bike', 'price': 999.99},
    }

    product = products.get(product_id)
    if not product:
        flash("Product not found.", "danger")
        return redirect(url_for('green_products'))

    if request.method == 'POST':
        # Get form data
        credit_card_number = request.form['credit_card_number']
        expiration_date = request.form['expiration_date']
        cvv = request.form['cvv']

        # Validate the credit card number (ensure it's 16 digits)
        if len(credit_card_number) != 16 or not credit_card_number.isdigit():
            flash("Invalid credit card number. It should be 16 digits.", "danger")
            return redirect(url_for('credit_card_product', product_id=product_id))

        # Validate expiration date (MM/YY format)
        expiration_parts = expiration_date.split('/')
        if len(expiration_parts) != 2 or not expiration_parts[0].isdigit() or not expiration_parts[1].isdigit():
            flash("Invalid expiration date. Use MM/YY format.", "danger")
            return redirect(url_for('credit_card_product', product_id=product_id))

        month, year = expiration_parts
        if not (1 <= int(month) <= 12) or len(year) != 2:
            flash("Invalid expiration date. Month must be between 01 and 12, and year should be in 2-digit format.", "danger")
            return redirect(url_for('credit_card_product', product_id=product_id))

        # Validate CVV (3 digits)
        if len(cvv) != 3 or not cvv.isdigit():
            flash("Invalid CVV. It should be 3 digits.", "danger")
            return redirect(url_for('credit_card_product', product_id=product_id))

        # Example: Simulate payment processing (in a real app, you'd integrate with a payment gateway)
        flash(f"Payment successful for {product['name']}! Total: ${product['price']}", "success")
        return redirect(url_for('green_products'))

    return render_template('credit_card_product.html', product=product)




# Green Products page
@app.route('/green_products')
def green_products():
    return render_template('green_products.html')


# Schedule Consultation page

@app.route('/schedule_consultation', methods=['GET', 'POST'])
def schedule_consultation():
    # Consultation types and their prices
    consultation_prices = {
        "Energy Efficiency": 100.00,
        "Carbon Footprint Analysis": 150.00,
        "Solar Panel Installation": 200.00,
        "Electric Vehicle Consultation": 250.00,
    }

    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        phone_number = request.form['phone_number']
        consultation_type = request.form['consultation_type']
        consultation_fee = consultation_prices.get(consultation_type)
        preferred_date = request.form['preferred_date']
        message = request.form['message']

        # Flash success message
        flash("Consultation scheduled successfully! Please proceed to payment.", "success")

        # Pass consultation details to the credit card page
        return redirect(url_for('credit_card_consultation',
                                consultation_type=consultation_type,
                                consultation_fee=consultation_fee))

    return render_template('schedule_consultation.html')


@app.route('/credit_card_consultation', methods=['GET', 'POST'])
def credit_card_consultation():
    consultation_type = request.args.get('consultation_type')
    consultation_fee = request.args.get('consultation_fee')

    # Error control - Initialize empty errors list
    errors = []

    if request.method == 'POST':
        # Get form data
        credit_card_number = request.form['credit_card_number']
        expiration_date = request.form['expiration_date']
        cvv = request.form['cvv']

        # Validate Credit Card Number (should be 16 digits)
        if len(credit_card_number) != 16 or not credit_card_number.isdigit():
            errors.append("Credit card number must be exactly 16 digits.")

        # Validate Expiration Date (MM/YY format)
        expiration_parts = expiration_date.split('/')
        if len(expiration_parts) != 2 or not expiration_parts[0].isdigit() or not expiration_parts[1].isdigit():
            errors.append("Expiration date should be in MM/YY format.")

        month, year = expiration_parts if len(expiration_parts) == 2 else ("", "")
        if not (1 <= int(month) <= 12) or len(year) != 2:
            errors.append("Invalid expiration month or year format.")

        # Validate CVV (should be 3 digits)
        if len(cvv) != 3 or not cvv.isdigit():
            errors.append("CVV must be exactly 3 digits.")

        # If there are errors, display them and prevent form submission
        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template('credit_card_consultation.html', consultation_type=consultation_type, consultation_fee=consultation_fee)

        # If no errors, process the payment
        flash(f"Payment successful for {consultation_type} consultation. Total: £{consultation_fee}", "success")
        return redirect(url_for('home'))  # Redirect to home or a confirmation page

    return render_template('credit_card_consultation.html', consultation_type=consultation_type, consultation_fee=consultation_fee)



if __name__ == "__main__":
    init_db()
    app.run(debug=True)
