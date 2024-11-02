from flask import Flask, request, session, render_template, url_for, jsonify, redirect, flash
from passlib.hash import sha256_crypt
import hashlib
import gc
from functools import wraps
import dbfunc, mysql.connector 
from datetime import datetime
 
app = Flask (__name__) #instantiating flask app
app.secret_key = 'Super Secret' #secret key for sessions 
#trying to get this page to prompt you to log in and after you're logged in return you to the bookings page 


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
    return render_template('userHome.html', username=session['username'])


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



@app.route('/register/', methods=['POST', 'GET'])
def register():
    error = ''
    print('Register start')
    try:
        if request.method == "POST":         
            username = request.form['username']
            password = request.form['password']                    
            if username != None and password != None:           
                conn = dbfunc.getConnection()
                if conn != None:    #Checking if connection is None           
                    if conn.is_connected(): #Checking if connection is established
                        print('MySQL Connection is established')                          
                        dbcursor = conn.cursor()    #Creating cursor object 
                        #here we should check if username / email already exists                                                           
                        password = sha256_crypt.hash((str(password)))          
                        Verify_Query = "SELECT * FROM users WHERE username = %s;"
                        dbcursor.execute(Verify_Query,(username,))
                        rows = dbcursor.fetchall() 
                        if dbcursor.rowcount > 0:   #this means there is a user with same name
                            print('username already taken, please choose another')
                            error = "User name already taken, please choose another"
                            return render_template("account2.html", error=error)    
                        else:   #this means we can add new user            
                            dbcursor.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, password))                
                            conn.commit()  #saves data in database              
                            print("Thanks for registering!")
                            dbcursor.close()
                            conn.close()
                            gc.collect()                        
                            session['logged_in'] = True     #session variables
                            session['username'] = username
                            session['usertype'] = 'standard'   #default all users are standard
                            return render_template("success.html",\
                             message='User registered successfully and logged in..')
                    else:                        
                        print('Connection error')
                        return 'DB Connection Error'
                else:                    
                    print('Connection error')
                    return 'DB Connection Error'
            else:                
                print('empty parameters')
                return render_template("account2.html", error=error)
        else:            
            return render_template("account2.html", error=error)        
    except Exception as e:                
        return render_template("account2.html", error=e)    
    return render_template("account2.html", error=error)


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

 
def admin_required(f): #do we even need an admin feature? what would they do?
    @wraps(f)
    def wrap(*args, **kwargs):
        if ('logged_in' in session) and (session['usertype'] == 'admin'):
            return f(*args, **kwargs)
        else:            
            print("You need to login first as admin user")
            return render_template('account2.html', error='You need to login first as admin user')    
    return wrap

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


#/adminfeatures is loaded for admin users
@app.route('/adminfeatures/')
@login_required
@admin_required
def admin_features():
        print('create / amend records / delete records / generate reports')
        #records from database can be derived, updated, added, deleted
        #user login can be checked..
        print ('Welcome ', session['username'], ' as ', session['usertype'])
        return render_template('adminuser.html', user=session['username'],\
             message='Admin data from app and admin features can go here ...')

    

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
    
    return render_template("addvalues.html")

@app.route('/addIncome', methods=['POST'])
@login_required
def add_income():
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
    except Exception as e:
        # Handle the error (e.g., log it, flash a message, etc.)
        flash(f"An error occurred: {str(e)}")
    finally:
        conn.close()  # Always close the connection

    return render_template('viewBudget.html')

@app.route('/addExpenses', methods=['POST'])
@login_required
def add_expenses():
    username = session['username']
    conn = dbfunc.getConnection()

    # Get expense details from the form
    expense_name = request.form.get('expense_name')
    expense_amount = request.form.get('expense_amount')

    # Insert expense into the expenses table
    with conn.cursor() as cursor:
        cursor.execute("""
            INSERT INTO expenses (username, expense_name, expense_amount)
            VALUES (%s, %s, %s);
        """, (username, expense_name, expense_amount))
        conn.commit()

    flash("Expense added successfully!")
    return render_template('viewBudget.html')

# Add Savings to Budget
@app.route('/addSavings', methods=['POST'])
@login_required
def add_savings():
    username = session['username']
    conn = dbfunc.getConnection()

    # Get the savings details from the form
    saving_name = request.form.get('saving_name')
    saving_amount = request.form.get('saving_amount')

    # Insert savings into the savings table
    with conn.cursor() as cursor:
        cursor.execute("""
            INSERT INTO savings (username, saving_name, saving_amount)
            VALUES (%s, %s, %s);
        """, (username, saving_name, saving_amount))
        conn.commit()

    flash("Savings added successfully!")
    return render_template('viewBudget.html')


@app.route('/addvalues/', methods=['GET', 'POST'])
@login_required
def add_financial_entries():
    username = session['username']

    if request.method == 'POST':
        # Determine which entry to add based on the button pressed
        if 'add_income' in request.form:
            return add_income()
        elif 'add_expense' in request.form:
            return add_expenses()
        elif 'add_saving' in request.form:
            return add_savings()

    return render_template('addvalues.html')  # Render the form template

@app.route('/view_budget')
@login_required
def view_budget():
    username = session['username']
    conn = dbfunc.getConnection()
    print("connection established")

    try:
        # Fetch budget details
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM budgets WHERE username = %s", (username,))
            budget = cursor.fetchone()
            print("found budget")

            # Check if a budget exists
            if not budget:
                flash("No budget found for this user.")
                print("there's no bduget")
                return redirect(url_for('create_budget'))  # Redirect to budget creation if none exists
            

            # Access budget fields by index
            budget_name = budget[2]  # Assuming budget_name is the third column
            budget_amount = budget[3]  # Assuming budget_amount is the fourth column
            savings = budget[4]  # Assuming savings is the fifth column

            cursor.execute("SELECT * FROM income WHERE username = %s", (username,))
            incomes = cursor.fetchall()
            print("income")

            cursor.execute("SELECT * FROM expenses WHERE username = %s", (username,))
            expenses = cursor.fetchall()
            print("expenses")

            cursor.execute("SELECT * FROM savings WHERE username = %s", (username,))
            savings = cursor.fetchall()
            print("savings")

        print("going to calculate")
        # Calculate totals using the correct indices
        # Calculate totals ensuring values are treated as numbers
        total_income = sum(float(income[3]) for income in incomes) if incomes else 0.0  # Convert to float
        total_expenses = sum(float(expense[3]) for expense in expenses) if expenses else 0.0  # Convert to float
        print("calculated")

    except Exception as e:
        flash(f"An error occurred while retrieving budget data: {str(e)}")
        return redirect(url_for('userHome'))  # Handle error appropriately

    finally:
        conn.close()  # Always close the connection

    # Render the template with all required data
    return render_template(
        'viewBudget.html',
        budget_name=budget_name,
        budget_amount=budget_amount,
        incomes=incomes,
        expenses=expenses,
        savings=savings,
        total_income=total_income,
        total_expenses=total_expenses
    )

#privacy page 
@app.route ('/privacyStatement') #inheritance: base.html
def privacyPage():
    return render_template ('privacy4.html')

#cookies page 
@app.route ('/cookies') #inheritance: base.html
def Cookies():
    return render_template ('cookies3.html')


#New booking page 
@app.route ('/bookings') #inheritance: secondbase.html
def newBookings():
    return render_template ('NewBookings.html') 



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