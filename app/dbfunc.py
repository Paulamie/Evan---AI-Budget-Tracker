import mysql.connector
from mysql.connector import errorcode
 
# MYSQL CONFIG VARIABLES
hostname    = "localhost"
username    = "root"
passwd  = "<An4>gonca"
db = "evan"

from flask import Flask

def create_app(testing=False):
    app = Flask(__name__)
    app.config['TESTING'] = testing

    # Register routes (adjust if you're using blueprints)
    from .routes import register_routes  # Example: move your route registrations here
    register_routes(app)

    return app

def getConnection():    
    try:
        conn = mysql.connector.connect(host=hostname,                              
                              user=username,
                              password=passwd,
                              database=db)  
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print('User name or Password is not working')
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print('Database does not exist')
        else:
            print(err)                        
    else:  #will execute if there is no exception raised in try block
        return conn   
                
