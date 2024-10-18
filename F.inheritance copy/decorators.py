from flask import Flask, request, session, render_template, url_for, jsonify, redirect
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
        print("running")
        if 'logged_in' in session:
            print("test 1")
            return f(*args, **kwargs)
        else: 
            print ("test 2")
            print("you need to log in first")
        return render_template('account2.html', error="you need to log in first")
    return wrap

#booking process:
#home page 
@app.route('/') #decorator/ endpoints
@app.route('/home/')
def homePage():
    conn = dbfunc.getConnection()
    if conn != None:    #Checking if connection is None         
        print('MySQL Connection is established')                          
        dbcursor = conn.cursor()    #Creating cursor object            
        dbcursor.execute('SELECT DISTINCT deptCity FROM routes;') #booking process starts here         
        rows = dbcursor.fetchall()                                    
        dbcursor.close()              
        conn.close() #Connection must be 
        cities = []
        for city in rows:
            city = str(city).strip("(")
            city = str(city).strip(")")
            city = str(city).strip(",")
            city = str(city).strip("'")
            cities.append(city)
    return render_template('home1.html', departurelist=cities)

@app.route ('/returncity/', methods = ['POST', 'GET'])
def ajax_returncity():   
	print('/returncity') 

	if request.method == 'GET':
		deptcity = request.args.get('q')
		conn = dbfunc.getConnection()
		if conn != None:    #Checking if connection is None                               
			dbcursor = conn.cursor()    #Creating cursor object            
			dbcursor.execute('SELECT DISTINCT arrivCity FROM routes WHERE deptCity = %s;', (deptcity,)) #gives the return options from the selected city              
			rows = dbcursor.fetchall()
			total = dbcursor.rowcount                                    
			dbcursor.close()              
			conn.close() #Connection must be closed			
			return jsonify(returncities=rows, size=total)
		else:
			print('DB connection Error')
			return jsonify(returncities='DB Connection Error') 

#display prices from the selected route 
@app.route ('/prices/', methods = ['POST', 'GET']) 
@login_required
def selectBooking():
    if request.method == 'POST':
        departcity = request.form['departureslist']
        arrivalcity = request.form['arrivalslist']
        arrivalcity = request.form['arrivalslist']
        outdate = request.form['outdate']
        returndate = request.form['returndate']
        adultseats = request.form['adultseats']
        childseats = request.form['childseats']
        
        
        
        lookupdata = [departcity, arrivalcity, outdate, returndate, adultseats, childseats]
        conn = dbfunc.getConnection()
        if conn != None:    #Checking if connection is None        
            print('MySQL Connection is established')                          
            dbcursor = conn.cursor()    #Creating cursor object         
            dbcursor.execute('SELECT * FROM routes WHERE deptCity = %s AND arrivCity = %s;', (departcity, arrivalcity))           
            rows = dbcursor.fetchall()
            datarows=[]			
            for row in rows:
                data = list(row)                    
                fare = (float(row[5]) * float(adultseats)) + (float(row[5]) * 0.5 * float(childseats))
                data.append(fare)
                datarows.append(data)			
            dbcursor.close()              
            conn.close() #Connection must be closed	
            return render_template('showPrices.html', resultset=datarows, lookupdata=lookupdata) 
    else: 
        print("something went wrong")
        return render_template ("NoPrice.html")

#display the receipt for the journey selected 
@app.route ('/booking_confirm/', methods = ['POST', 'GET']) 
def booking_confirm():
    if request.method == 'POST':		
        print('booking confirm initiated')
        journeyid = request.form['bookingchoice']	
        departcity = request.form['deptcity']
        arrivalcity = request.form['arrivcity']
        outdate = request.form['outdate']
        returndate = request.form['returndate']
        adultseats = request.form['adultseats']
        childseats = request.form['childseats']
        totalfare = request.form['totalfare']
        cardnumber = request.form['cardnumber']
        classes = request.form ['classes']
        
        totalseats = int(adultseats) + int(childseats)
        bookingdata = [journeyid, departcity, arrivalcity, outdate, returndate, adultseats, childseats, totalfare, classes]
        print(bookingdata)
        conn = dbfunc.getConnection()
        if conn != None:    #Checking if connection is None         
            print('MySQL Connection is established')                          
            dbcursor = conn.cursor()    #Creating cursor object     	
            dbcursor.execute('INSERT INTO bookings (deptDate, arrivDate, idRoutes, noOfSeats, classes, totFare) VALUES \
				(%s, %s, %s, %s, %s, %s);', (outdate, returndate, journeyid, totalseats, classes, totalfare))   
            print('Booking statement executed successfully.')             
            conn.commit()	
            dbcursor.execute('SELECT LAST_INSERT_ID();')    
            rows = dbcursor.fetchone()
            bookingid = rows[0]
            bookingdata.append(bookingid)
            dbcursor.execute('SELECT * FROM routes WHERE idRoutes = %s;', (journeyid,))   			
            rows = dbcursor.fetchall()
            deptTime = rows[0][2]
            arrivTime = rows[0][4]
            bookingdata.append(deptTime)
            bookingdata.append(arrivTime)
            cardnumber = cardnumber[-4:-1]
            print(cardnumber)
            dbcursor.execute
            dbcursor.close()              
            conn.close() #Connection must be closed
            return render_template('booking_confirm.html', resultset=bookingdata, cardnumber=cardnumber)
        else:
            print('DB connection Error')
            return redirect(url_for('index')) 

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

#starting the log in process hopefully

#here the user should be prompted to sign up/ log in - this is before they get their receipt 

@app.route('/home/<usertype>') #display contents depending on if user is admin or standard 
def homepage(usertype):
    return render_template ('account2.html', usertype=usertype)

# My account page
@app.route ('/myAccount/') #inherirance:base.html
def myAccount():
    return render_template ('account2.html') 

@app.route('/register/', methods=['POST', 'GET'])
def register():
    error = ''
    print('Register start')
    try:
        if request.method == "POST":         
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']                      
            if username != None and password != None and email != None:           
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
                            dbcursor.execute("INSERT INTO users (username, password_hash, \
                                 email) VALUES (%s, %s, %s)", (username, password, email))                
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
    if 'logged_in' == True:
        return redirect(url_for)
    try:	
        if request.method == "POST":            
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
                                return render_template('userresources.html', \
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

def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if ('logged_in' in session) and (session['usertype'] == 'admin'):
            return f(*args, **kwargs)
        else:            
            print("You need to login first as admin user")
            #return redirect(url_for('login', error='You need to login first as admin user'))
            return render_template('account2.html', error='You need to login first as admin user')    
    return wrap

def standard_user_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if ('logged_in' in session) and (session['usertype'] == 'standard'):
            return f(*args, **kwargs)
        else:            
            print("You need to login first as standard user")
            #return redirect(url_for('login', error='You need to login first as standard user'))
            return render_template('account2.html', error='You need to login first as standard user')    
    return wrap

#/logout is to log out of the system.
@app.route("/logout/")
@login_required
def logout():    
    session.clear()    #clears session variables
    print("You have been logged out!")
    gc.collect()
    return render_template('home1.html', optionalmessage='You have been logged out')

#/userfeatures is loaded for standard users
@app.route('/userfeatures/')
@login_required
@standard_user_required
def user_features():
        print('fetchrecords')
        #records from database can be derived
        #user login can be checked..
        print ('Welcome ', session['username'])
        return render_template('standarduser.html', \
            user=session['username'], message='User data from app and standard \
                user features can go here....')

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

#/generateadminreport is loaded for admin users only
@app.route('/generateadminreport/',methods = ["POST", "GET"])
@login_required
@admin_required
def generate_admin_report():
    error = ''
    print('admin record start')
    try:
        if request.method == "POST": 
            print('test1')      
            idroute = request.form['journeyid']		   
            print ('test2')  #couldn't get to this point. Error message display: 400 Bad Request: The browser (or proxy) sent a request that this server could not understand.     
            conn = dbfunc.getConnection()
            if conn != None:    #Checking if connection is None           
                if conn.is_connected(): #Checking if connection is established
                    print('MySQL Connection is established')                          
                    dbcursor = conn.cursor()    #Creating cursor object 
                    #here we should check if username / email already exists                                                                    
                    sql_query = "SELECT * FROM bookings WHERE idRoutes = %s;"
                    dbcursor.execute(sql_query,(idroute,))
                    records = dbcursor.fetchall()           
                    if len(records) > 0:   #this means it exits
                        print("<table>")
                        print("<tr><th>ID</th><th>Column 1</th><th>Column 2</th></tr>")
                        for row in records:
                            return render_template("adminreport2.html", records=records)
                    else:
                        print("0 results")
                        return render_template("adminreport2.html",\
                            message='0 results')
                else:                        
                        print('Connection error')
                        return 'DB Connection Error'
            else:                    
                    print('Connection error')
                    return 'DB Connection Error'
        else:            
            return render_template("adminreport.html", error=error)    
    except Exception as e:                
        return render_template("adminreport.html", error=e)     
#the page where admin can choose to add, delete or update a journey, price or user records.
@app.route('/journeyrecord/')
@login_required
@admin_required
def records():
    print('create / amend records / delete records')
    print ('Welcome ', session['username'], ' as ', session['usertype'])
    return render_template('records.html', user=session['username'])

#admin update a journey 
@app.route('/updatejourney', methods = ["POST", "GET"])
@login_required
@admin_required
def update_journey():
    error = ''
    print('update journey start')
    try:
        if request.method == "POST": 
            print('test1')      
            idroute = request.form['journeyid']		
            departcity = request.form['deptcity']
            arrivalcity = request.form['arrivcity']
            depttime= request.form['depttime']  
            arrivtime = request.form['arrivtime']    
            stFares = request.form ['stFares']   
            classes = request.form ['classes']           
            print ('test2')  #couldn't get to this point. Error message display: 400 Bad Request: The browser (or proxy) sent a request that this server could not understand.     
            conn = dbfunc.getConnection()
            if conn != None:    #Checking if connection is None           
                if conn.is_connected(): #Checking if connection is established
                    print('MySQL Connection is established')                          
                    dbcursor = conn.cursor()    #Creating cursor object 
                    #here we should check if username / email already exists                                                                    
                    Verify_Query = "SELECT * FROM routes WHERE idRoutes = %s;"
                    dbcursor.execute(Verify_Query,(idroute,))
                    rows = dbcursor.fetchall()           
                    if dbcursor.rowcount <= 0:   #this means the journey id doesn't exists
                        print('journey  do not exist')
                        error = "journey do not exist"
                        return render_template("journeyup.html", error=error)    
                    else:   #this means we can update journey            
                        dbcursor.execute("UPDATE routes SET deptCity = %s, arrivCity = %s, deptTime = %s, arrivTime = %s, stFare = %s, classes = %s WHERE idRoutes = %s ", (departcity, arrivalcity, depttime, arrivtime, stFares, classes, idroute))                
                        conn.commit()  #saves data in database              
                        print("Thanks for updating this journey!")
                        dbcursor.close()
                        conn.close()
                        gc.collect()                        
                        return render_template("journeyup2.html",\
                            message='Journey updated successfully')
                else:                        
                        print('Connection error')
                        return 'DB Connection Error'
            else:                    
                    print('Connection error')
                    return 'DB Connection Error'
        else:            
            return render_template("journeyup.html", error=error)        
    except Exception as e:                
        return render_template("journeyup.html", error=e) 

#admin adds journey 
@app.route('/addjourney', methods = ["POST", "GET"])
@login_required
@admin_required
def add_journey():
    error = ''
    print('add journey start')
    try:
        if request.method == "POST": 
            print('test1')    
            idroute = request.form['journeyid']		
            departcity = request.form['deptcity']
            arrivalcity = request.form['arrivcity']
            depttime= request.form['depttime']  
            arrivtime = request.form['arrivtime'] 
            stFares = request.form ['stFares']   
            classes = request.form ['classes']       
            print ('test2')  #can't get to this function: 400 Bad Request: The browser (or proxy) sent a request that this server could not understand.
            conn = dbfunc.getConnection()
            if conn != None:    #Checking if connection is None           
                if conn.is_connected(): #Checking if connection is established
                    print('MySQL Connection is established')                          
                    dbcursor = conn.cursor()    #Creating cursor object 
                    #here we should check if username / email already exists                                                                    
                    Verify_Query = "SELECT * FROM routes WHERE idRoutes = %s;"
                    dbcursor.execute(Verify_Query,(idroute,))
                    rows = dbcursor.fetchall()           
                    if dbcursor.rowcount > 0:   #this means the journey id already exists
                        print('journey already exist')
                        error = "journey already exist"
                        return render_template("addjourney.html", error=error)    
                    else:   #this means we can update journey            
                        dbcursor.execute('INSERT INTO routes (idRoutes, deptCity, deptTime, arrivCity, arrivTime, stFare, classes) VALUES (%s, %s, %s, %s, %s, %s, %s);', (idroute, departcity, depttime, arrivalcity, arrivtime, stFares, classes,)) 
                        conn.commit()  #saves data in database              
                        print("Thank you for adding this journey!")
                        dbcursor.close()
                        conn.close()
                        gc.collect()                        
                        return render_template("addjourney2.html",\
                            message='Journey added successfully')
                else:                        
                        print('Connection error')
                        return 'DB Connection Error'
            else:                    
                    print('Connection error')
                    return 'DB Connection Error'
        else:            
            return render_template("addjourney.html", error=error)        
    except Exception as e:                
        return render_template("addjourney.html", error=e) 


@app.route('/deljourney', methods = ["POST", "GET"])
@login_required
@admin_required
def delete_journey():
    error = ''
    print('delete journey start')
    try:
        if request.method == "POST": 
            print('test1')    
            idroute = request.form['idRoute']		        
            print ('test2')  #can't get to this function: 400 Bad Request: The browser (or proxy) sent a request that this server could not understand.
            conn = dbfunc.getConnection()
            if conn != None:    #Checking if connection is None           
                if conn.is_connected(): #Checking if connection is established
                    print('MySQL Connection is established')                          
                    dbcursor = conn.cursor()    #Creating cursor object 
                    #here we should check if username / email already exists                                                                    
                    Verify_Query = "SELECT * FROM routes WHERE idRoutes = %s;"
                    dbcursor.execute(Verify_Query,(idroute,))
                    rows = dbcursor.fetchall()           
                    if dbcursor.rowcount == 0:   #this means the journey don't exist
                        print('journey dont exist')
                        error = "journey does not exist"
                        return render_template("deljourney.html", error=error)    
                    else:   #this means we can delete journey            
                        dbcursor.execute("DELETE FROM routes WHERE idRoutes = %s;", (idroute,)) 
                        conn.commit()  #saves data in database              
                        print("journey deleted")
                        dbcursor.close()
                        conn.close()
                        gc.collect()                        
                        return render_template("deljourney2.html",\
                            message='Journey deleted successfully')
                else:                        
                        print('Connection error')
                        return 'DB Connection Error'
            else:                    
                    print('Connection error')
                    return 'DB Connection Error'
        else:            
            return render_template("deljourney.html", error=error)        
    except Exception as e:                
        return render_template("deljourney.html", error=e) 

@app.route('/pricerec/')
@login_required
@admin_required
def pricerec():
    print ('Welcome ', session['username'], ' as ', session['usertype'])
    return render_template('pricerec.html', user=session['username'])    
    
#admin update prices 
@app.route('/updateprice', methods = ["POST", "GET"])
@login_required
@admin_required
def update_prices():
    error = ''
    print('update price start')
    try:
        if request.method == "POST": 
            print('test1')      
            idroute = request.form['journeyid']		
            stFares = request.form['stFares']
            print ('test2')  
            print('journeyid', idroute)
            conn = dbfunc.getConnection()
            if conn != None:    #Checking if connection is None           
                if conn.is_connected(): #Checking if connection is established
                    print('MySQL Connection is established')                          
                    dbcursor = conn.cursor()    #Creating cursor object 
                    #here we should check if route exist                                                                    
                    Verify_Query = "SELECT * FROM routes WHERE idRoutes = %s"  #issue:1064 (42000): You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near '%s' at line 1
                    print('journeyid', idroute)
                    dbcursor.execute(Verify_Query,(idroute,))
                    rows = dbcursor.fetchall()           
                    if dbcursor.rowcount == 0:   #this means the journey id doesn't exists
                        print('journey  do not exist')
                        error = "journey do not exist"
                        return render_template("journeyup.html", error=error)  #change template  
                    else:   #this means we can update journey            
                        dbcursor.execute("UPDATE routes SET stFare=%s WHERE idRoutes = %s", (stFares, idroute,))                
                        conn.commit()  #saves data in database              
                        print("Thanks for updating this journey!")
                        dbcursor.close()
                        conn.close()
                        gc.collect()                        
                        return render_template("priceup2.html",\
                            message='Price updated successfully')
                else:                        
                        print('Connection error')
                        return 'DB Connection Error'
            else:                    
                    print('Connection error')
                    return 'DB Connection Error'
        else:            
            return render_template("priceup.html", error=error)        
    except Exception as e:   
        print("Error: ", e)
        print("SQL Query: ", dbcursor.statement)
        print("Variables: ", (stFares, idroute))             
        return render_template("priceup.html", error=e) 

@app.route('/userrec/')
@login_required
@admin_required
def userrec():
    print ('Welcome ', session['username'], ' as ', session['usertype'])
    return render_template('userrec.html', user=session['username'])    

@app.route('/updateuser', methods = ["POST", "GET"])
@login_required
@admin_required
def update_user():
    error = ''
    print('update user start')
    try:
        if request.method == "POST": 
            print('test1')      
            id = request.form['id']		
            username = request.form['username']
            email = request.form['email']
            password= request.form['password']  
            usertype = request.form['usertype']           
            print ('test2')  
            conn = dbfunc.getConnection()
            if conn != None:    #Checking if connection is None           
                if conn.is_connected(): #Checking if connection is established
                    print('MySQL Connection is established')                          
                    dbcursor = conn.cursor()    #Creating cursor object 
                    #here we should check if username / email already exists 
                    password = sha256_crypt.hash((str(password)))                                                                   
                    Verify_Query = "SELECT * FROM users WHERE id = %s;"
                    dbcursor.execute(Verify_Query,(id,))
                    rows = dbcursor.fetchall()           
                    if dbcursor.rowcount == 0:   #this means the journey id doesn't exists
                        print('user  do not exist')
                        error = "user does not exist"
                        return render_template("userup.html", error=error)    
                    else:   #this means we can update journey            
                        dbcursor.execute("UPDATE users SET username = %s, email = %s, password_hash = %s, usertype =%s WHERE id = %s ", (username, email, password, usertype,id))                
                        conn.commit()  #saves data in database              
                        print("Thanks for updating this user!")
                        dbcursor.close()
                        conn.close()
                        gc.collect()                        
                        return render_template("userup2.html", message='User updated successfully')
                else:                        
                        print('Connection error')
                        return 'DB Connection Error'
            else:                    
                    print('Connection error')
                    return 'DB Connection Error'
        else:            
            return render_template("userup.html", error=error)        
    except Exception as e:                
        return render_template("userup.html", error=e) 

#admin adds user
@app.route('/adduser', methods = ["POST", "GET"]) 
@admin_required
def add_user():
    error = ''
    print('add user start')
    try:
        if request.method == "POST": 
            print('test1')    
            username = request.form['username']
            email = request.form['email']
            password= request.form['password']  
            usertype = request.form['usertype']             
            print ('test2')  
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
                    print("test 3")       
                    if dbcursor.rowcount > 0:   #this means the user id already exists
                        print("test 4")
                        print('user already exist')
                        error = "username already exist"
                        return render_template("adduser.html", error=error)    
                    else:   #this means we can update user  
                        print ("test 5")          
                        dbcursor.execute('INSERT INTO users (username, email, password_hash, usertype) VALUES (%s, %s, %s, %s);', (username, email, password, usertype,)) 
                        conn.commit()  #saves data in database    
                        print ("test 6")          
                        print("Thank you for adding this user!")
                        dbcursor.close()
                        conn.close()
                        gc.collect()    
                        print ("test 7")                    
                        return render_template("adduser2.html",\
                            message='User added successfully')
                else:                        
                        print('Connection error')
                        return 'DB Connection Error'
            else:                    
                    print('Connection error')
                    return 'DB Connection Error'
        else:            
            return render_template("adduser.html", error=error)        
    except Exception as e:                
        return render_template("adduser.html", error=e) 


@app.route('/deluser', methods = ["POST", "GET"]) 
@login_required
@admin_required
def delete_user():
    error = ''
    print('delete user start')
    try:
        if request.method == "POST": 
            id = request.form['id']		       
            conn = dbfunc.getConnection()
            if conn != None:    #Checking if connection is None           
                if conn.is_connected(): #Checking if connection is established
                    print('MySQL Connection is established')                          
                    dbcursor = conn.cursor()    #Creating cursor object 
                    #here we should check if username / email already exists                                                                    
                    Verify_Query = "SELECT * FROM users WHERE id = %s" 
                    dbcursor.execute(Verify_Query,(id,))
                    rows = dbcursor.fetchall()           
                    if dbcursor.rowcount == 0:   #this means the user don't exist
                        print('journey dont exist')
                        error = "user does not exist"
                        return render_template("deluser.html", error=error)    
                    else:   #this means we can delete user    
                        dbcursor.execute("DELETE FROM users WHERE id = %s;", (id,)) 
                        conn.commit()  #saves data in database              
                        print("user deleted")
                        dbcursor.close()
                        conn.close()
                        gc.collect()                        
                        return render_template("deluser2.html",\
                            message='User deleted successfully')
                else:                        
                        print('Connection error')
                        return 'DB Connection Error'
            else:                    
                    print('Connection error')
                    return 'DB Connection Error'
        else:            
            return render_template("deluser.html", error=error)        
    except Exception as e:                
        return render_template("deluser.html", error=e) 
    
    
    
    
    
    
    
    
#updates the password for the Admins
@app.route('/updatePassword/', methods = ["POST", "GET"])
@login_required
@admin_required
def update_admin_password():
    error = ''
    print('update start')
    try:
        if request.method == "POST": #can't get inside tbis function for some reason
            print('test1')
            username = request.form['username']        
            password = request.form['password']                 
            if  password != None: 
                print ('test2')          
                conn = dbfunc.getConnection()
                if conn != None:    #Checking if connection is None           
                    if conn.is_connected(): #Checking if connection is established
                        print('MySQL Connection is established')                          
                        dbcursor = conn.cursor()    #Creating cursor object 
                        #here we should check if username exists                                                         
                        password = sha256_crypt.hash((str(password)))           
                        Verify_Query = "SELECT * FROM users WHERE username = %s;"
                        dbcursor.execute(Verify_Query,(username,))
                        rows = dbcursor.fetchall()           
                        if dbcursor.rowcount == 0:   #this means that the username doesn't exist
                            print('username do not exist')
                            error = "Please try again, username does not exist"
                            return render_template("changepassword.html", error=error)    
                        else:   #this means we can add new user             
                            dbcursor.execute("UPDATE users SET password_hash =%s WHERE username = %s", (password, username))                
                            conn.commit()  #saves data in database              
                            print("Thanks for updating your password!")
                            dbcursor.close()
                            conn.close()
                            gc.collect()                        
                            return render_template("change2.html", message='Password updated successfully')
                    else:                        
                        print('Connection error')
                        return 'DB Connection Error'
                else:                    
                    print('Connection error')
                    return 'DB Connection Error'
            else:                
                print('empty parameters')
                return render_template("changepassword.html", error=error)
        else:            
            return render_template("changepassword.html", error=error)        
    except Exception as e:                
        return render_template("changepassword.html", error=e) 

#/generateuserrecord is loaded for standard users only
@app.route('/generateuserrecord/')
@login_required
@standard_user_required
def generate_user_record():
    print('User records')
    #here you can generate required data as per business logic
    return """
        <h1> this is User record for user {} </h1> 
        <a href='/userfeatures')> Go to User Features page </a>
    """.format(session['username']) #how can i make the history of a user booking be displayed here?
    #initial thought: during booking process user is required to log in and then we put the system to save that booking under the 
    



#update bookings details from the user's perspective
@app.route('/editbooking/', methods = ["POST", "GET"])
@login_required
@standard_user_required
def edit_booking():
    error = ''
    print('edit booking start')
    try:
        print(request.form)
        if request.method == "POST": #can't get inside this function
            print('test1')       
            bookingid = request.form['bookingid']
            departure = request.form['departure']
            returning = request.form['returning']   
            NoPassengers = request.form['NoPassengers']   
                        
            print ('test2')          
            conn = dbfunc.getConnection()
            if conn != None:    #Checking if connection is None           
                if conn.is_connected(): #Checking if connection is established
                    print('MySQL Connection is established')                          
                    dbcursor = conn.cursor()    #Creating cursor object 
                        #here we should check if username / email already exists                                                                 
                    Verify_Query = "SELECT * FROM bookings WHERE idBooking = %s;"
                    dbcursor.execute(Verify_Query,(bookingid,))
                    rows = dbcursor.fetchall()           
                    if dbcursor.rowcount == 0:   #this means the booking don't exist
                        print('booking doesnt exist')
                        error = "booking number incorrect"
                        return render_template("updateb.html", error=error)    
                    else:   #this means we can edit the details            
                        dbcursor.execute("UPDATE bookings SET deptDate = %s, arrivDate = %s, noOfSeats = %s WHERE idBooking = %s", (departure, returning, NoPassengers, bookingid,))                
                        conn.commit()  #saves data in database              
                        print("Thanks for updating your Booking")
                        dbcursor.close()
                        conn.close()
                        gc.collect()                        
                        return render_template("updateb2.html",\
                            message='Booking updated successfully')
                else:                        
                    print('Connection error')
                    return 'DB Connection Error'
            else:                    
                print('Connection error')
                return 'DB Connection Error'
        else:                
            print('empty parameters')
            return render_template("updateb.html", error=error)    
    except Exception as e:                
        return render_template("updateb.html", error=e)  
    
#update user data -> all in one page write new name, email, password and then tell the database to update details.
@app.route('/updateInfo/', methods = ["POST", "GET"])
@login_required
@standard_user_required
def update_user_data():
    error = ''
    print('update start')
    try:
        if request.method == "POST": #can't get inside this function
            print('test1')       
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']                      
            if username != None and password != None and email != None: 
                print ('test2')          
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
                        if dbcursor.rowcount == 0:   #this means the user don't exist
                            print('username not found, please enter your username')
                            error = "username not found, please enter your username"
                            return render_template("update.html", error=error)    
                        else:   #this means we can edit the details            
                            dbcursor.execute("UPDATE users SET password_hash = %s, email = %s WHERE username = %s", (password, email, username))                
                            conn.commit()  #saves data in database              
                            print("Thanks for updating your details!")
                            dbcursor.close()
                            conn.close()
                            gc.collect()                        
                            session['logged_in'] = True     #session variables
                            session['username'] = username
                            session['usertype'] = 'standard'   #default all users are standard
                            return render_template("successupdate.html",\
                             message='User updated successfully')
                    else:                        
                        print('Connection error')
                        return 'DB Connection Error'
                else:                    
                    print('Connection error')
                    return 'DB Connection Error'
            else:                
                print('empty parameters')
                return render_template("update.html", error=error)
        else:            
            return render_template("update.html", error=error)        
    except Exception as e:                
        return render_template("update.html", error=e)  


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