from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import requests
from datetime import datetime

app = Flask(__name__)

# Firebase database URL for load cell data (update this with your actual database URL)
firebase_db_url = "https://pantryplus-b207e-default-rtdb.asia-southeast1.firebasedatabase.app/loadCell.json"

# Database connection function
def get_db_connection():
    conn = sqlite3.connect('groceries.db')
    conn.row_factory = sqlite3.Row  # This helps with accessing columns by name
    return conn

# Function to create the groceries table if it doesn't exist
def create_db():
    conn = sqlite3.connect('groceries.db')
    cursor = conn.cursor()
    
    # Create the groceries table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS groceries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        weight REAL NOT NULL,
        expiry DATE NOT NULL
    )
    ''')
    
    # Commit changes and close the connection
    conn.commit()
    conn.close()

# Call create_db() to ensure the database and table are created
create_db()

# Route to fetch load cell data from Firebase
@app.route('/get-load-cell-data', methods=['GET'])
def get_load_cell_data():
    try:
        # Make a GET request to the Firebase database
        response = requests.get(firebase_db_url)
        response.raise_for_status()  # Raise an HTTPError for bad responses

        # Return the Firebase data as a JSON response
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        # Print error to console for debugging
        print(f"Error fetching data from Firebase: {e}")
        return jsonify({"error": "Failed to fetch data from Firebase"}), 500

# Home page
@app.route('/')
def home():
    return render_template('home.html')

# Add new grocery
@app.route('/add-grocery', methods=['GET', 'POST'])
def add_grocery():
    if request.method == 'POST':
        name = request.form['name']
        weight = request.form['weight']
        expiry = request.form['expiry']
        
        # Insert the new grocery item into the database
        conn = get_db_connection()
        conn.execute('INSERT INTO groceries (name, weight, expiry) VALUES (?, ?, ?)',
                     (name, weight, expiry))
        conn.commit()
        conn.close()
        
        return redirect(url_for('home'))  # Redirect to home page after successful addition
    
    return render_template('add_grocery.html')

# Update grocery
@app.route('/update-grocery', methods=['GET', 'POST'])
def update_grocery():
    if request.method == 'POST':
        # Get the data from the form
        grocery_id = request.form['id']
        new_weight = request.form['weight']
        new_expiry = request.form['expiry']
        
        # Ensure that the data is correctly converted to float for weight
        try:
            new_weight = float(new_weight)
        except ValueError:
            return "Invalid weight value", 400  # Return an error if the weight is not a valid number
        
        # Update the grocery item's weight and expiry date in the database
        conn = get_db_connection()
        conn.execute('UPDATE groceries SET weight = ?, expiry = ? WHERE id = ?',
                     (new_weight, new_expiry, grocery_id))
        conn.commit()
        conn.close()
        
        return redirect(url_for('home'))  # Redirect to home page after successful update
    
    # Fetch all groceries for the dropdown list
    conn = get_db_connection()
    groceries = conn.execute('SELECT * FROM groceries').fetchall()
    conn.close()
    
    return render_template('update_grocery.html', groceries=groceries)

# Stock levels (view all groceries with sorting)
@app.route('/stock-levels', methods=['GET'])
def stock_levels():
    # Get the sorting parameter from the query string, default to 'expiry'
    sort_by = request.args.get('sort-by', 'expiry')

    conn = get_db_connection()
    groceries = conn.execute('SELECT * FROM groceries').fetchall()  # Fetch all groceries from the database
    conn.close()
    
    # Sort groceries based on the selected option
    if sort_by == 'expiry':
        groceries = sorted(groceries, key=lambda x: x['expiry'])  # Sort by expiry date
    elif sort_by == 'weight':
        groceries = sorted(groceries, key=lambda x: x['weight'])  # Sort by weight

    # Check if any grocery is below 100g and set a notification
    low_stock_items = []
    expiring_items = []
    current_date = datetime.today().date()

    for grocery in groceries:
        if grocery['weight'] < 100:
            low_stock_items.append(grocery['name'])  # Store names of low-stock items
        # Check for expiring soon (you can adjust this to your needs)
        if datetime.strptime(grocery['expiry'], '%Y-%m-%d').date() <= current_date:
            expiring_items.append(grocery['name'])  # Store names of expiring items
    
    # Set a notification for low-stock and expiring items
    notification = None
    if low_stock_items or expiring_items:
        low_stock_message = f"Low stock items: {', '.join(low_stock_items)}" if low_stock_items else ""
        expiring_message = f"Expiring soon: {', '.join(expiring_items)}" if expiring_items else ""
        
        notification = f"{low_stock_message} | {expiring_message}".strip(' |')
    
    # Render the stock_levels.html template and pass the groceries data along with notification and sort option
    return render_template('stock_levels.html', groceries=groceries, notification=notification, sort_by=sort_by)

# Delete grocery
@app.route('/delete-grocery', methods=['GET', 'POST'])
def delete_grocery():
    if request.method == 'POST':
        grocery_id = request.form['id']
        
        # Delete the grocery item from the database
        conn = get_db_connection()
        conn.execute('DELETE FROM groceries WHERE id = ?', (grocery_id,))
        conn.commit()
        conn.close()
        
        return redirect(url_for('home'))  # Redirect to home page after successful deletion
    
    # Fetch all groceries for the dropdown list
    conn = get_db_connection()
    groceries = conn.execute('SELECT * FROM groceries').fetchall()
    conn.close()
    
    return render_template('delete_grocery.html', groceries=groceries)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)