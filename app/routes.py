from flask import Flask, request, session, render_template, url_for, jsonify, redirect, flash
from passlib.hash import sha256_crypt
import hashlib
import gc
from functools import wraps
import dbfunc
import mysql.connector
from datetime import datetime
import tensorflow as tf
from tensorflow import keras
import numpy as np
import string
import re
from flask_mysqldb import MySQL
import os

mysql = MySQL()
app = Flask (__name__)
app.secret_key = 'your_secret_key_here'

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else: 
            print("you need to log in first")
        return render_template('account2.html', error="you need to log in first")
    return wrap

# home Page
@app.route('/') #decorator/ endpoints
def myAccount():
    return render_template ('account2.html') 

@app.route('/userhome/')
def userHome():
    username = session.get('username', 'Guest')
    username = session['username']
    conn = dbfunc.getConnection()

    try:
        # Fetch budget details
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM budgets WHERE username = %s", (username,))
            budget = cursor.fetchone()

            # Check if a budget exists
            if not budget:
                flash("No budget created")

            cursor.execute("SELECT * FROM income WHERE username = %s", (username,))
            incomes = cursor.fetchall()

            cursor.execute("SELECT * FROM expenses WHERE username = %s", (username,))
            expenses = cursor.fetchall()

            cursor.execute("SELECT * FROM savings WHERE username = %s", (username,))
            savings = cursor.fetchall()

        # Calculate totals
        total_income = sum(float(income[3]) for income in incomes) if incomes else 0.0  # Convert to float
        total_expenses = sum(float(expense[3]) for expense in expenses) if expenses else 0.0  # Convert to float
        total_savings = sum(float(savings[3]) for savings in savings) if savings else 0.0  # Convert to float
        
        print("calculated")

    finally:
        conn.close()  # Always close the connection
        
    return render_template(
        'userHome.html', 
        username=username,
        total_income=total_income,
        total_expenses=total_expenses,
        total_savings=total_savings
    )

############################################################################################################################
@app.route ('/dumpsVar/', methods = ['POST', 'GET']) #i'm not sure we need this 
def dumpVar():
	if request.method == 'POST':
		result = request.form
		output = "<H2>Data Received: </H2></br>"
		output += "Number of Data Fields : " + str(len(result))
		for key in list(result.keys()):
			output = output + " </br> " + key + " : " + result.get(key)
		return output
	else:
		result = request.args
		output = "<H2>Data Received: </H2></br>"
		output += "Number of Data Fields : " + str(len(result))
		for key in list(result.keys()):
			output = output + " </br> " + key + " : " + result.get(key)
		return output  

@app.route('/home/<usertype>') #display contents depending on if user is admin or standard 
def homepage(usertype):
    return render_template ('account2.html', usertype=usertype)


###############################################################################################################
@app.route('/register/', methods=['POST'])
def register():
    error = ''
    try:
        if request.method == "POST":
            username = request.form.get('username')
            raw_password = request.form.get('password')

            if not username or not raw_password:
                error = "Username/password missing."
                return render_template("account2.html", error=error)

            # 1) Validate raw password (NOT hashed!)
            if not validate_password(raw_password):
                error = "Password must be at least 8 chars, with uppercase, lowercase, and a digit."
                return render_template("account2.html", error=error)

            conn = dbfunc.getConnection()
            if conn and conn.is_connected():
                dbcursor = conn.cursor()

                # Check if username already exists
                dbcursor.execute("SELECT * FROM users WHERE username = %s", (username,))
                rows = dbcursor.fetchall()
                if dbcursor.rowcount > 0:
                    error = "User name already taken. Choose another."
                    return render_template("account2.html", error=error)

                # 2) Hash only after it passes validation
                hashed_pass = sha256_crypt.hash(str(raw_password))

                # 3) Insert into DB
                dbcursor.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                                 (username, hashed_pass))
                conn.commit()

                dbcursor.close()
                conn.close()

                session['logged_in'] = True
                session['username'] = username
                session['usertype'] = 'standard'
                return render_template("userHome.html", message="User registered successfully and logged in.")

            else:
                return "DB Connection Error"
        else:
            return render_template("account2.html", error=error)
    except Exception as e:
        return render_template("account2.html", error=e)

def validate_password(password):
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    return True


#/login/ route receives user name and password and checks against db user/pw
@app.route('/login/', methods=["GET","POST"])
def login():
    form={}
    error = ''
    print("1")
    if 'logged_in' in session and session['logged_in']:
        return redirect(url_for('userHome'))
    try:	
        if request.method == "POST":  
            print("3")          
            username = request.form['username']
            password = request.form['password']            
            form = request.form
            print('login start 1.1')
            
            if username != None and password != None:  #check if un or pw is none          
                conn = dbfunc.getConnection()
                if conn != None:    #Checking if connection is None                    
                    if conn.is_connected(): #Checking if connection is established                        
                        print('MySQL Connection is established')                          
                        dbcursor = conn.cursor()    #Creating cursor object                                                 
                        dbcursor.execute("SELECT password_hash, usertype \
                            FROM users WHERE username = %s;", (username,))                                                
                        data = dbcursor.fetchone()
                        print(data[0])
                        if dbcursor.rowcount == 0: #this mean no user exists                         
                            error = "User / password does not exist, login again"
                            return render_template("account2.html", error=error)
                        else:                            
                            #data = dbcursor.fetchone()[0] #extracting password   
                            # verify passowrd hash and password received from user                                                             
                            if sha256_crypt.verify(request.form['password'], str(data[0])): #having problems with this bit, it says that the Sha. Invalid credentials                               
                                session['logged_in'] = True     #set session variables
                                session['username'] = request.form['username']
                                session['usertype'] = str(data[1])                          
                                print("You are now logged in")                                
                                return render_template('userHome.html', \
                                    username=username, data='this is user specific data',\
                                         usertype=session['usertype'])
                            else:
                                error = "Invalid credentials username/password, try again."                               
                    gc.collect()
                    print('login start 1.10')
                    return render_template("account2.html", form=form, error=error)
    except Exception as e:                
        error = str(e) + " <br/> Invalid credentials, try again."
        return render_template("account2.html", form=form, error = error)   
    
    return render_template("account2.html", form=form, error = error)
 

def standard_user_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if ('logged_in' in session) and (session['usertype'] == 'standard'):
            return f(*args, **kwargs)
        else:            
            print("You need to login first as standard user")
            return render_template('account2.html', error='You need to login first as standard user')    
    return wrap


#/logout is to log out of the system.
@app.route("/logout/")
@login_required
def logout():    
    session.clear()    #clears session variables
    print("You have been logged out!")
    gc.collect()
    return render_template('account2.html', optionalmessage='You have been logged out')

#######################################################################################################################################


    
#######################################################################################################################################
@app.route('/createBudget/', methods=['GET', 'POST'])
@login_required
def create_budget():
    username = session['username']
    conn = dbfunc.getConnection()

    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT budgets.id 
            FROM budgets
            JOIN users ON users.username = budgets.username
            WHERE users.username = %s;
        """, (username,))
        existing_budget = cursor.fetchone()

    if existing_budget:
        return render_template('userHome.html', error="You can only have one main budget.")
    
    # Get budget details from form inputs directly
    amount = request.form.get('budget[amount]')
    name = request.form.get('budget[name]')
    
    if not amount or not name:
        return render_template('records.html', error="Please provide both budget amount and name.")
    
    with conn.cursor() as cursor:
        cursor.execute("""
            INSERT INTO budgets (username, budget_amount, budget_name)
            SELECT username, %s, %s FROM users WHERE username = %s
        """, (amount, name, username))
        conn.commit()
    
    return render_template("success.html")

#######################################################################################################################################
@app.route('/addIncome', methods=['GET', 'POST'])
@login_required
def add_income():
    if request.method == 'POST':
        username = session['username']
        conn = dbfunc.getConnection()

        # Get income details from the form
        income_source = request.form.get('income_source')
        income_amount = request.form.get('income_amount')

        try:
            # Insert income into the income table
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO income (username, income_source, income_amount)
                    VALUES (%s, %s, %s);
                """, (username, income_source, income_amount))
                conn.commit()

            flash("Income added successfully!")
            return redirect(url_for('view_budget'))  # Redirect to the viewBudget function
        except Exception as e:
            # Handle the error (e.g., log it, flash a message, etc.)
            flash(f"An error occurred: {str(e)}")
        finally:
            conn.close()  # Always close the connection

    return render_template('addIncome.html')  # Render the income form for GET requests

@app.route('/addExpenses', methods=['GET', 'POST'])
@login_required
def add_expenses():
    if request.method == 'POST':
        username = session['username']
        conn = dbfunc.getConnection()

        # Get expense details from the form
        expense_name = request.form.get('expense_name')
        expense_amount = request.form.get('expense_amount')

        try:
            # Insert expense into the expenses table
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO expenses (username, expense_name, expense_amount)
                    VALUES (%s, %s, %s);
                """, (username, expense_name, expense_amount))
                conn.commit()

            flash("Expense added successfully!")
            return redirect(url_for('view_budget'))  # Redirect to the viewBudget function
        except Exception as e:
            # Handle the error (e.g., log it, flash a message, etc.)
            flash(f"An error occurred: {str(e)}")
        finally:
            conn.close()  # Always close the connection

    return render_template('addExpenses.html')  # Render the expenses form for GET requests

# Add Savings to Budget
@app.route('/addSavings', methods=['GET', 'POST'])
@login_required
def add_savings():
    if request.method == 'POST':
        username = session['username']
        conn = dbfunc.getConnection()

        # Get the savings details from the form
        saving_name = request.form.get('saving_name')
        saving_amount = request.form.get('saving_amount')

        try:
            # Insert savings into the savings table
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO savings (username, saving_name, saving_amount)
                    VALUES (%s, %s, %s);
                """, (username, saving_name, saving_amount))
                conn.commit()

            flash("Savings added successfully!")
            return redirect(url_for('view_budget'))  # Redirect to the viewBudget function
        except Exception as e:
            # Handle the error (e.g., log it, flash a message, etc.)
            flash(f"An error occurred: {str(e)}")
        finally:
            conn.close()  # Always close the connection

    return render_template('addSavings.html')  # Render the savings form for GET requests

#######################################################################################################################################
@app.route('/view_budget')
@login_required
def view_budget():
    username = session['username']
    conn = dbfunc.getConnection()

    try:
        # Fetch budget details
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM budgets WHERE username = %s", (username,))
            budget = cursor.fetchone()

            # Check if a budget exists
            if not budget:
                flash("No budget found for this user.")
                return redirect(url_for('create_budget'))  # Redirect to budget creation if none exists

            cursor.execute("SELECT * FROM income WHERE username = %s", (username,))
            incomes = cursor.fetchall()

            cursor.execute("SELECT * FROM expenses WHERE username = %s", (username,))
            expenses = cursor.fetchall()

            cursor.execute("SELECT * FROM savings WHERE username = %s", (username,))
            savings = cursor.fetchall()

        # Calculate totals
        total_income = sum(float(income[3]) for income in incomes) if incomes else 0.0  # Convert to float
        total_expenses = sum(float(expense[3]) for expense in expenses) if expenses else 0.0  # Convert to float
        total_savings = sum(float(savings[3]) for savings in savings) if savings else 0.0  # Convert to float
        
        #Calculate total budget amount
        total_budget_amount = total_income + total_savings
        
        # Calculate remaining budget
        remaining_budget = total_budget_amount - total_expenses
        

    except Exception as e:
        flash(f"An error occurred while retrieving budget data: {str(e)}")
        return redirect(url_for('userHome'))  # Handle error appropriately

    finally:
        conn.close()  # Always close the connection

    # Prepare budget details
    budget_name = budget[2]
    budget_amount = float(budget[3])
    
    # Prepare savings details with proper keys for id, name, and amount
    savings_list = [{'id': saving[0], 'name': saving[2], 'amount': float(saving[3])} for saving in savings]

    # Render the template with all required data
    return render_template(
        'viewBudget.html',
        budget_name=budget_name,
        budget_amount=budget_amount,
        savings=savings_list,
        incomes=incomes,
        expenses=expenses,
        total_budget_amount = total_budget_amount,
        remaining_budget = remaining_budget,
        total_income=total_income,
        total_expenses=total_expenses,
        total_savings=total_savings
    )

#######################################################################################################################################
@app.route('/deleteIncome/<int:income_id>', methods=['POST'])
@login_required
def delete_income(income_id):
    conn = dbfunc.getConnection()
    username = session['username']

    try:
        # Delete the income record by ID and username (ensuring username is correctly matched as a VARCHAR)
        with conn.cursor() as cursor:
            cursor.execute("""
                DELETE FROM income
                WHERE id = %s AND username = %s;
            """, (income_id, username))
            conn.commit()

        flash("Income entry deleted successfully!")
    except Exception as e:
        flash(f"An error occurred: {str(e)}")
    finally:
        conn.close()

    return redirect(url_for('view_budget'))


@app.route('/deleteExpense/<int:expense_id>', methods=['POST'])
@login_required
def delete_expense(expense_id):
    conn = dbfunc.getConnection()
    username = session['username']

    try:
        # Delete the expense record by ID and username
        with conn.cursor() as cursor:
            cursor.execute("""
                DELETE FROM expenses
                WHERE id = %s AND username = %s;
            """, (expense_id, username))
            conn.commit()

        flash("Expense entry deleted successfully!")
    except Exception as e:
        flash(f"An error occurred: {str(e)}")
    finally:
        conn.close()

    return redirect(url_for('view_budget'))

@app.route('/deleteSaving/<int:saving_id>', methods=['POST'])
@login_required
def delete_saving(saving_id):
    conn = dbfunc.getConnection()
    username = session['username']

    try:
        # Delete the saving record by ID and username
        with conn.cursor() as cursor:
            cursor.execute("""
                DELETE FROM savings
                WHERE id = %s AND username = %s;
            """, (saving_id, username))
            conn.commit()

        flash("Saving entry deleted successfully!")
    except Exception as e:
        flash(f"An error occurred: {str(e)}")
    finally:
        conn.close()

    return redirect(url_for('view_budget'))

#######################################################################################################################################
# Update user data -> Update password
@app.route('/userAccount', methods=["POST", "GET"])
@login_required
@standard_user_required
def update_user_data():
    error = ''
    print('Update process started')
    try:
        if request.method == "POST":
            # Retrieve form data
            username = request.form.get('username')
            password = request.form.get('password')

            if username and password:  # Check for non-empty inputs
                print('Valid username and password received')

                conn = dbfunc.getConnection()
                if conn and conn.is_connected():  # Ensure the database connection is established
                    print('MySQL Connection established')
                    dbcursor = conn.cursor()                 
                    
                    if not validate_password(password):
                        error = "Password must be at least 8 chars, include uppercase, lowercase, and a digit."
                        return render_template("useraccount.html", error=error)

                    # Hash the new password
                    hashed_password = sha256_crypt.hash(str(password))
                    password = request.form['password']


                    # Check if the user exists
                    verify_query = "SELECT * FROM users WHERE username = %s;"
                    dbcursor.execute(verify_query, (username,))
                    user_exists = dbcursor.fetchone()  # Check if any result exists

                    if not user_exists:
                        error = "Username not found, please enter a valid username."
                        print(error)
                        return render_template("useraccount.html", error=error)
                    else:
                        # Update the password in the database
                        update_query = "UPDATE users SET password_hash = %s WHERE username = %s"
                        dbcursor.execute(update_query, (hashed_password, username))
                        conn.commit()  # Save changes to the database

                        print("Password updated successfully!")
                        dbcursor.close()
                        conn.close()
                        gc.collect()

                        # Update session variables
                        session['logged_in'] = True
                        session['username'] = username
                        session['usertype'] = 'standard'  # Default user type

                        # Display success message
                        return render_template("useraccount.html", message="Password updated successfully!")
                else:
                    error = "Database connection error. Please try again later."
                    print(error)
                    return render_template("useraccount.html", error=error)
            else:
                error = "Username or password cannot be empty."
                print(error)
                return render_template("useraccount.html", error=error)
        else:
            # Render the user account page for GET requests
            return render_template("useraccount.html", error=error)
    except Exception as e:
        error = f"An error occurred: {str(e)}"
        print(error)
        return render_template("useraccount.html", error=error)
    
def validate_password(password):
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    return True

#######################################################################################################################################


model_path = os.path.join(os.path.dirname(__file__), '..', 'spending_model_tf.h5')
model_path = os.path.abspath(model_path)  
model = keras.models.load_model(model_path)

def predict_user_spending_tf(username):
    conn = dbfunc.getConnection()
    with conn.cursor() as cursor:
        # Retrieve the user’s last month’s total expenses
        cursor.execute("""
            SELECT SUM(expense_amount)
            FROM expenses
            WHERE username=%s
              AND MONTH(created_at) = MONTH(CURDATE())
              AND YEAR(created_at) = YEAR(CURDATE());
        """, (username,))
        last_month_expenses = cursor.fetchone()[0] or 0.0

        # Retrieve last month’s total income
        cursor.execute("""
            SELECT SUM(income_amount)
            FROM income
            WHERE username=%s
              AND MONTH(created_at) = MONTH(CURDATE())
              AND YEAR(created_at) = YEAR(CURDATE());
        """, (username,))
        last_month_income = cursor.fetchone()[0] or 0.0

    conn.close()

    # Convert to np array matching the model's input shape (batch_size=1, features=2)
    X_current = np.array([[last_month_expenses, last_month_income]], dtype=float)
    
    # Use the TensorFlow model to predict
    predicted_array = model.predict(X_current)
    predicted_value = predicted_array[0][0]  # single value

    return round(predicted_value, 2)

def advice_on_expenses(user_expenses, predicted_next_month):
    advice_list = []

    # If no user_expenses data, we cannot compare with last month's spending:
    if not user_expenses:
        advice_list.append("Keep going, we don’t have any advice for you this month due to no previous data.")
        return advice_list

    # The most recent expense record is user_expenses[0] if sorted descending
    last_month_spent = user_expenses[0]['amount']

    # 1) If predicted is significantly higher than average of last 3 months + 100
    #    (the existing logic)
    if len(user_expenses) >= 3:
        # Sum of the last 3 entries
        last_three_sum = sum(e['amount'] for e in user_expenses[:3])
        last_three_avg = last_three_sum / 3.0
        if predicted_next_month > last_three_avg + 100:
            advice_list.append(
                "Your expenses seem to be growing quickly. Consider reviewing monthly subscriptions or bigger expense categories."
            )

    # 2) Compare predicted_next_month with the single last month's spending:
    #    If predicted is lower or the same => "You are doing great!"
    if predicted_next_month <= last_month_spent:
        advice_list.append(
            "You are doing great! Your predicted expenses are the same or lower than last month's."
        )
    else:
        # If it's higher than last month, add a smaller-scale caution message
        advice_list.append(
            "Your next month's expenses may be higher than last month’s. Try tracking your biggest categories and see where you can save!"
        )

    return advice_list

#page for the reports/ user patterns 
@app.route('/report')
@login_required
def view_report():
    username = session['username']
    
    conn = dbfunc.getConnection()

    with conn.cursor() as cursor:
        # Example queries
        cursor.execute("SELECT budget_name, budget_amount FROM budgets WHERE username = %s", (username,))
        budget_data = cursor.fetchone()  # (budget_name, budget_amount)

        cursor.execute("SELECT SUM(expense_amount) FROM expenses WHERE username = %s", (username,))
        total_expenses_data = cursor.fetchone()  # (sum_of_expenses)

        cursor.execute("SELECT expense_name, expense_amount, DATE(created_at) as date FROM expenses WHERE username = %s ORDER BY created_at DESC", (username,))
        expenses_data = cursor.fetchall()
    conn.close()
    
    expenses_list = [
        {'name': row[0], 'amount': float(row[1]), 'date': row[2]} 
        for row in expenses_data
    ]

    predicted_expenses = predict_user_spending_tf(username)
    advice_list = advice_on_expenses(expenses_list, predicted_expenses)
    
    return render_template(
        'reports.html',
        budget_name=budget_data[0],
        budget_amount=float(budget_data[1]),
        total_expenses=float(total_expenses_data[0]) if total_expenses_data[0] else 0.0,
        expenses=expenses_list,
        predicted_expenses=predicted_expenses,
        advice_list=advice_list,
    )

#######################################################################################################################################
def get_month_range(year, month, past=1, future=1):
    start_year = year - past
    start_month = month

    end_year = year + future
    end_month = month

    current_y = start_year
    current_m = start_month

    # We'll go until we surpass (end_year, end_month)
    while (current_y < end_year) or (current_y == end_year and current_m <= end_month):
        yield (current_y, current_m)
        current_m += 1
        if current_m == 13:
            current_m = 1
            current_y += 1
  
@app.route ('/calendarView')
@login_required
def calendar():
    username = session['username']
    conn = dbfunc.getConnection()

    # 1-year range from current date
    current_year = datetime.now().year
    current_month = datetime.now().month

    # Build dictionary for 1 year in the past and 1 year in the future
    # e.g., from (current_year - 1, current_month) to (current_year + 1, current_month)
    calendar_data = {}

    with conn.cursor() as cursor:
        # For each month in that range:
        # We'll use a function to loop from (current_year-1, current_month) to (current_year+1, current_month)
        for (year, month) in get_month_range(current_year, current_month, past=1, future=1):
            # Key: yyyy-mm
            ym_key = f"{year}-{str(month).zfill(2)}"

            # Query for expenses in that month
            cursor.execute("""
                SELECT expense_name, expense_amount, DATE(created_at)
                FROM expenses
                WHERE username = %s
                AND MONTH(created_at) = %s
                AND YEAR(created_at) = %s
                ORDER BY created_at
            """, (username, month, year))
            expense_rows = cursor.fetchall()
            # Convert to list of dictionaries
            expense_list = []
            for row in expense_rows:
                expense_list.append({
                    "name": row[0],
                    "amount": float(row[1]),
                    "date": str(row[2])  # e.g., '2025-03-15'
                })

            # Query for income
            cursor.execute("""
                SELECT income_source, income_amount, DATE(created_at)
                FROM income
                WHERE username = %s
                AND MONTH(created_at) = %s
                AND YEAR(created_at) = %s
                ORDER BY created_at
            """, (username, month, year))
            income_rows = cursor.fetchall()
            income_list = []
            for row in income_rows:
                income_list.append({
                    "name": row[0],
                    "amount": float(row[1]),
                    "date": str(row[2])
                })

            # Insert into calendar_data
            calendar_data[ym_key] = {
                "expenses": expense_list,
                "income": income_list
            }

    return render_template(
        'calendar.html',
        calendar_data=calendar_data
    )
    
#######################################################################################################################################
#investement tracking page 
@app.route('/investments', methods=['GET','POST'])
@login_required
def investments():
    username = session['username']
    conn = dbfunc.getConnection()

    # Suppose we read the user's objective from a form or query param
    # If none is provided, default to 'dividends' or something
    objective = request.form.get('objective', 'dividends')

    # Build the user's portfolio
    user_stocks = {}
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT symbol, quantity
                FROM stocks_owned
                WHERE username = %s;
            """, (username,))
            rows = cursor.fetchall()
            for row in rows:
                symbol = row[0]
                qty = row[1]
                user_stocks[symbol] = qty
    finally:
        conn.close()

    # Get recommended stocks + advice for owned stocks
    recommended_stocks, owned_advice = investment_advice(objective, user_stocks)

    # Convert owned_stocks dict to a list of objects to display
    owned_list = []
    for sym, qty in user_stocks.items():
        suggestion = owned_advice.get(sym, "Hold")
        owned_list.append({
            "symbol": sym,
            "quantity": qty,
            "suggestion": suggestion
        })

    return render_template(
        'investment.html',  
        user_stocks=owned_list,
        recommended_stocks=recommended_stocks,
        objective=objective
    )
    
@app.route('/investments/addStock', methods=['POST'])
@login_required
def add_stock():
    username = session['username']

    symbol = request.form['stockSymbol'].strip().upper()
    qty_str = request.form['stockQty'].strip()

    # Basic validation
    try:
        quantity = int(qty_str)
        if quantity <= 0:
            raise ValueError("Quantity must be > 0")
    except ValueError:
        flash("Invalid quantity.")
        return redirect(url_for('investments'))

    conn = dbfunc.getConnection()
    try:
        with conn.cursor() as cursor:
            # Insert or update row
            cursor.execute("""
                INSERT INTO stocks_owned (username, symbol, quantity)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE quantity = quantity + VALUES(quantity);
            """, (username, symbol, quantity))
            conn.commit()
    finally:
        conn.close()

    flash(f"Added {quantity} shares of {symbol}")
    return redirect(url_for('investments'))
    
@app.route('/investments/sellStock', methods=['POST'])
@login_required
def sell_stock():
    username = session['username']
    symbol = request.form['symbol'].strip().upper()

    conn = dbfunc.getConnection()
    try:
        with conn.cursor() as cursor:
            # Delete the stock from the user's holdings
            cursor.execute("""
                DELETE FROM stocks_owned 
                WHERE username = %s AND symbol = %s;
            """, (username, symbol))
            conn.commit()
    finally:
        conn.close()

    flash(f"You have sold all your shares of {symbol}.")
    return redirect(url_for('investments'))    

#mock up - simple algorithm to track stocks - Over time, i can integrate real stock data (Yahoo Finance API, Alpaca, etc.) and store user trades in my own database.
def investment_advice(objective, user_portfolio):
    """
    Provide a list of recommended stocks based on the user's investment objective,
    and also return advice for each stock the user already owns.

    :param objective: str indicating the user's investment goal.
                      e.g. 'dividends', 'variety', 'highRisk', 'lowRisk'.
    :param user_portfolio: dict mapping { 'symbol': quantity_owned, ... }.
    :return:
        recommended_stocks: list of dicts with fields
          { 'symbol', 'price', 'growth_1w', 'growth_1m', 'growth_1y', 'reason' },
        owned_advice: dict mapping { symbol: advice_string, ... } for the user's current holdings.
    """

    # A more detailed mock dataset with price & growth stats
    mock_stocks = {
      # Dividends (3-4 examples)
      'T': {
          'dividend': 'high', 
          'risk': 'low',
          'price': 19.50, 
          'growth_1w': -0.5, 
          'growth_1m': 2.0, 
          'growth_1y': 5.5
      },
      'KO': {
          'dividend': 'steady', 
          'risk': 'low',
          'price': 60.10, 
          'growth_1w': 1.2, 
          'growth_1m': 1.5, 
          'growth_1y': 8.0
      },
      'PM': {
          'dividend': 'high',
          'risk': 'medium',
          'price': 96.40,
          'growth_1w': 0.0,
          'growth_1m': 2.5,
          'growth_1y': 4.5
      },

      # Variety (3-4 examples: broad ETFs, different sectors)
      'VTI': {
          'dividend': 'moderate', 
          'risk': 'medium',
          'price': 210.30, 
          'growth_1w': 2.0, 
          'growth_1m': 3.5, 
          'growth_1y': 10.0
      },
      'VXUS': {
          'dividend': 'moderate',
          'risk': 'medium',
          'price': 54.20,
          'growth_1w': -0.3,
          'growth_1m': 1.1,
          'growth_1y': 5.7
      },
      'SCHD': {
          'dividend': 'steady',
          'risk': 'medium',
          'price': 74.90,
          'growth_1w': 0.8,
          'growth_1m': 2.0,
          'growth_1y': 7.0
      },

      # High risk (3-4 examples)
      'TSLA': {
          'dividend': 'none', 
          'risk': 'high',
          'price': 200.50, 
          'growth_1w': 5.0, 
          'growth_1m': 15.0, 
          'growth_1y': -10.0
      },
      'ARKK': {
          'dividend': 'none',
          'risk': 'high',
          'price': 38.75,
          'growth_1w': 3.2,
          'growth_1m': 10.1,
          'growth_1y': -20.0
      },
      'COIN': {
          'dividend': 'none',
          'risk': 'high',
          'price': 65.10,
          'growth_1w': 4.0,
          'growth_1m': 12.5,
          'growth_1y': -30.0
      },

      # Low risk (3-4 examples)
      'BND': {
          'dividend': 'steady', 
          'risk': 'low',
          'price': 74.60, 
          'growth_1w': 0.1, 
          'growth_1m': 0.5, 
          'growth_1y': 2.0
      },
      'BRK.B': {
          'dividend': 'none', 
          'risk': 'low',
          'price': 310.00, 
          'growth_1w': 1.8, 
          'growth_1m': 3.2, 
          'growth_1y': 14.5
      },
      'KO': {  # repeating KO as an example, or you can add something else
          'dividend': 'steady', 
          'risk': 'low',
          'price': 60.10, 
          'growth_1w': 1.2, 
          'growth_1m': 1.5, 
          'growth_1y': 8.0
      }
    }

    # We'll build a list of recommended stocks with relevant fields
    recommended_stocks = []

    # Example logic for each objective
    for symbol, data in mock_stocks.items():
        # High dividend preference
        if objective == 'dividends':
            # user wants high or steady dividend
            if data['dividend'] in ['high', 'steady']:
                recommended_stocks.append({
                    'symbol': symbol,
                    'price': data['price'],
                    'growth_1w': data['growth_1w'],
                    'growth_1m': data['growth_1m'],
                    'growth_1y': data['growth_1y'],
                    'reason': f"Good for dividends ({data['dividend']})"
                })

        elif objective == 'variety':
            # For a naive approach, let's pick "medium" risk ETFs or multiple sectors
            if data['risk'] in ['medium']:
                recommended_stocks.append({
                    'symbol': symbol,
                    'price': data['price'],
                    'growth_1w': data['growth_1w'],
                    'growth_1m': data['growth_1m'],
                    'growth_1y': data['growth_1y'],
                    'reason': f"Broader market or balanced approach"
                })

        elif objective == 'highRisk':
            if data['risk'] == 'high':
                recommended_stocks.append({
                    'symbol': symbol,
                    'price': data['price'],
                    'growth_1w': data['growth_1w'],
                    'growth_1m': data['growth_1m'],
                    'growth_1y': data['growth_1y'],
                    'reason': "Potential for big growth, but also bigger risk"
                })

        elif objective == 'lowRisk':
            if data['risk'] in ['low'] and data['dividend'] != 'none':
                recommended_stocks.append({
                    'symbol': symbol,
                    'price': data['price'],
                    'growth_1w': data['growth_1w'],
                    'growth_1m': data['growth_1m'],
                    'growth_1y': data['growth_1y'],
                    'reason': f"Steadier approach with {data['dividend']} dividend"
                })

    # Build advice for the user's owned portfolio
    owned_advice = {}
    for owned_symbol, qty in user_portfolio.items():
        data = mock_stocks.get(owned_symbol, {
            'risk': 'unknown', 'dividend': 'unknown',
            'price': 0.0,      # fallback defaults
            'growth_1w': 0.0,
            'growth_1m': 0.0,
            'growth_1y': 0.0
        })

        # 1) If user has fewer than 5 shares, we still say "Buy more?"
        if qty < 5:
            owned_advice[owned_symbol] = "Buy more?"
            continue

        # 2) If user has a large position in a high-risk stock
        if data['risk'] == 'high' and qty >= 10:
            owned_advice[owned_symbol] = (
                "You have a large high-risk holding—consider selling some?"
            )
            continue

        # 3) Otherwise, let's do a naive predicted monthly growth
        predicted_next_month_growth = (
            data['growth_1w'] +
            data['growth_1m'] +
            (data['growth_1y'] / 12.0)
        ) / 3.0

        if predicted_next_month_growth > 0.5:
            # If it's significantly positive
            owned_advice[owned_symbol] = (
                f"The stock shows growth potential. It might keep rising. "
                f"Consider selling now to realize gains, or hold if you want more growth."
            )
        elif predicted_next_month_growth < -0.5:
            # If it's a strong negative number
            owned_advice[owned_symbol] = (
                f"The stock may drop in value soon. "
                f"Either prepare for the dip or consider selling now to minimize losses."
            )
        else:
            # If it's between -0.5% and +0.5% or so, treat it as “no big change”
            owned_advice[owned_symbol] = (
                f"No significant change expected. 'Hold' your position."
            )

    return recommended_stocks, owned_advice




#######################################################################################################################################
#Chat bot Evan 

def get_user_budget(username, conn):
    """
    Returns a dictionary with the user's budget information, including:
        - budget_name
        - budget_amount
        - total_income (sum of 'income_amount' in 'income' table)
        - total_expenses (sum of 'expense_amount' in 'expenses' table)
        - leftover = total_income - total_expenses
        - budgets_table_savings (value from 'budgets.savings' column)
        - sum_of_savings_table (sum of 'saving_amount' in 'savings' table)
    """
    budget_data = {
        'budget_name': None,
        'budget_amount': 0.0,    
        'total_income': 0.0,
        'total_expenses': 0.0,
        'leftover': 0.0,
        'sum_of_savings_table': 0.0      # Sum of entries in the 'savings' table
    }

    with conn.cursor() as cursor:
        # 1) Fetch the single row from `budgets`
        cursor.execute("""
            SELECT budget_name, budget_amount
            FROM budgets
            WHERE username = %s
            LIMIT 1;
        """, (username,))
        row = cursor.fetchone()
        if row:
            budget_data['budget_name'] = row[0]
            budget_data['budget_amount'] = float(row[1])
    

        # 2) Sum incomes
        cursor.execute("""
            SELECT COALESCE(SUM(income_amount), 0)
            FROM income
            WHERE username = %s;
        """, (username,))
        row = cursor.fetchone()
        total_income = float(row[0]) if row else 0.0
        budget_data['total_income'] = total_income

        # 3) Sum expenses
        cursor.execute("""
            SELECT COALESCE(SUM(expense_amount), 0)
            FROM expenses
            WHERE username = %s;
        """, (username,))
        row = cursor.fetchone()
        total_expenses = float(row[0]) if row else 0.0
        budget_data['total_expenses'] = total_expenses

        # 4) Sum leftover: (income - expenses)
        leftover = total_income - total_expenses
        budget_data['leftover'] = leftover

        # 5) Sum from the `savings` table
        cursor.execute("""
            SELECT COALESCE(SUM(saving_amount), 0)
            FROM savings
            WHERE username = %s;
        """, (username,))
        row = cursor.fetchone()
        sum_of_savings_table = float(row[0]) if row else 0.0
        budget_data['sum_of_savings_table'] = sum_of_savings_table

    return budget_data

def get_user_stocks(username, conn):
    """
    Returns a dict mapping {symbol: quantity, ...}
    for the user's owned stocks from 'stocks_owned'.
    """
    stocks = {}
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT symbol, quantity
            FROM stocks_owned
            WHERE username = %s;
        """, (username,))
        for row in cursor.fetchall():
            symbol = row[0]
            qty = row[1]
            stocks[symbol] = qty
    return stocks


@app.route('/evan', methods=['GET','POST'])
@login_required
def evan():
    username = session['username']
    
    # load conversation (list of messages) from session
    conversation = session.get('conversation', [])
    # load a 'conversation_state' dict from session for storing user’s objective, etc.
    conversation_state = session.get('evan_state', {})

    conn = dbfunc.getConnection()
    user_budget = get_user_budget(username, conn)
    user_stocks = get_user_stocks(username, conn)

    if request.method == 'POST':
        user_message = request.form.get('user_message', '').strip()
        if user_message:
            # add user message to conversation
            conversation.append({'role': 'user', 'text': user_message})

            # generate chatbot reply
            assistant_reply = chat_evan_response(
                user_message,
                user_budget,
                user_stocks,
                conversation_state
            )
            # add assistant reply
            conversation.append({'role': 'assistant', 'text': assistant_reply})

        # update session
        session['conversation'] = conversation
        session['evan_state'] = conversation_state
        session.modified = True
        
        conn.close()

    return render_template('evanChat.html', conversation=conversation)

def normalize_word(w):
    """Remove trailing punctuation (like >, ., etc.) and convert to lower."""
    return w.strip(string.punctuation).lower()

def chat_evan_response(user_message, budget, stocks, conversation_state):
   
    text_lower = user_message.lower()
    words = text_lower.split()

    # Extract relevant budget info
    leftover = budget.get('leftover', 0.0)
    total_income = budget.get('total_income', 0.0)
    total_expenses = budget.get('total_expenses', 0.0)

    # Summarize user’s holdings
    if stocks:
        holdings_summary = ", ".join(f"{sym} ({qty} shares)" for sym, qty in stocks.items())
    else:
        holdings_summary = "You currently own no stocks."

    # 1. Possibly detect user’s objective 
    # e.g. "my objective is highrisk" or "i want dividends"
    possible_objectives = ["dividends","variety","highrisk","lowrisk"]
    if ("my objective is" in text_lower) or ("i want" in text_lower):
        for obj in possible_objectives:
            if obj in text_lower:
                conversation_state["objective"] = obj
                return f"Noted! I've set your objective to **{obj}**. Let me know if you have other questions."

    # get the user’s current objective, if set
    user_objective = conversation_state.get("objective", None)

    # 2. Check for queries about leftover or budget
    if "leftover" in text_lower or "budget" in text_lower:
        return (f"Your monthly budget leftover is £{leftover:.2f}. You earn £{total_income:.2f} "
                f"and spend £{total_expenses:.2f}. Let me know if you'd like advice on "
                "reducing expenses or increasing your income.")

    # 3. Check for reduce expenses or overspend
    if any(word in text_lower for word in ["reduce expenses", "cut costs", "overspend"]):
        return ("Here are some suggestions to reduce expenses:\n"
                "1) Track your spending categories.\n"
                "2) Eliminate or downgrade unused subscriptions.\n"
                "3) Plan meals at home instead of frequent dining out.\n"
                "Let me know if you need more specific tips.")

    # 4. Check for increase income
    if any(word in text_lower for word in ["increase income","earn more","side hustle"]):
        return ("To increase your income, consider:\n"
                "1) Negotiating a raise.\n"
                "2) Freelancing or side hustle.\n"
                "3) Selling unused items.\n"
                "4) Investing in new skills.\n"
                "Let me know if you have a preference on approach.")

    # 5. Check for stock or invest queries
    if "stock" in text_lower or "invest" in text_lower:
        return (f"{holdings_summary} If you're unsure whether to buy or sell, let me know your goals. "
                f"Currently, your objective is {user_objective or 'not specified'}.")

    # 6. Detect if user references a specific symbol or buy/sell
    known_symbols = ["tsla","arkk","t","ko","bnd","vti","vxus","brk.b","pm","schd","coin"]
    user_symbol = None
    for w in words:
        cleaned = normalize_word(w)
        if cleaned in known_symbols:
            user_symbol = cleaned.upper()
            break

    if user_symbol:
        # check if user said "buy" or "sell"
        if "sell" in text_lower:
            # do they own it?
            if user_symbol in [sym.upper() for sym in stocks.keys()]:
                return (f"You want to sell {user_symbol}? If you feel the price is up or it's too risky, "
                        f"selling is an option. Also consider how it fits your objective: {user_objective or 'what is your objective?'}.")
            else:
                return f"You don't currently own {user_symbol}, so there's nothing to sell."
        elif "buy" in text_lower:
            return (f"Thinking about buying {user_symbol}? Ensure it aligns with your leftover budget "
                    f"and your objective: {user_objective or 'none'}.")
        else:
            # user just referencing symbol
            return (f"{user_symbol} might fit your objective ({user_objective or 'not set'}). "
                    "What would you like to do—buy, sell, or learn more?")

    # 7. Fallback
    return ("I’m here to help with your budget, investments, or general financial tips—"
            "could you clarify what you'd like to know? You can ask about 'leftover' budget, "
            "'reduce expenses', 'increase income', or specify 'my objective is X'.")
    
@app.route('/evan/clear', methods=['POST'])
@login_required
def clear_chat():
    # Empty the conversation
    session['conversation'] = []
    flash("Chat cleared.")
    return redirect(url_for('evan'))




#######################################################################################################################################

#privacy page 
@app.route ('/privacyStatement')
def privacyPage():
    return render_template ('privacy4.html')

#cookies page 
@app.route ('/cookies')
def Cookies():
    return render_template ('cookies3.html')


#######################################################################################################################################
#debuggers
if __name__ == '__main__':   
   app.run(port=8000,debug = True)
   
if __name__ == '__main__':    #you can skip this if running app on terminal window
    for i in range(13000, 18000):
      try:
         app.run(debug = True, port = i)
         break
      except OSError as e:
         print("Port {i} not available".format(i))