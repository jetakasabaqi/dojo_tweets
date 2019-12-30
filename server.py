from flask import Flask, render_template, request, redirect, flash, session
from mysqlconnection import connectToMySQL
from flask_bcrypt import Bcrypt 
import re
app = Flask(__name__)
app.secret_key='secret'
bcrypt = Bcrypt(app) 
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')  
PASSWORD_REGEX = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{5,}$')
@app.route("/")
def index():
    if 'userid' in session:
        return redirect('/success')
        
    else:
        return render_template('registration.html')

@app.route("/create-user", methods=["POST"])
def add_friend_to_db():
    print(request.form)
    is_valid = True
    
    if len(request.form['firstName']) < 1:
    	is_valid = False
    	flash("Please enter a first name")
    if not (request.form['firstName']).isalpha():
    	is_valid = False
    	flash("First Name must only contain letters!")
    if len(request.form['lastName']) < 1:
    	is_valid = False
    	flash("Please enter a last name")
    if not (request.form['lastName']).isalpha():
    	is_valid = False
    	flash("Last Name must only contain letters!")
    if not EMAIL_REGEX.match(request.form['email']):   
        is_valid = False
        flash("Invalid email address!")
    if not PASSWORD_REGEX.match(request.form['password']):   
        is_valid = False
        flash("Password must have at least 5 characters, one number, one uppercase character, one special symbol.")
    if request.form['password'] != request.form['password_confirm']:
    	is_valid = False
    	flash("Password and Confirm Password should match")
    
    if is_valid:
        flash("Succesfully registered!")
        mysql = connectToMySQL("basic_registration")
        pw_hash = bcrypt.generate_password_hash(request.form['password'])  
        data ={
            'fn': request.form['firstName'],
            'ln': request.form['lastName'],
            'em': request.form['email'],
            'psw': pw_hash
        }
        
        query = "INSERT INTO users(first_name, last_name, email,password) VALUES(%(fn)s, %(ln)s,%(em)s, %(psw)s);"
        result = mysql.query_db(query, data)
        if result:
            print(result)
            session['userid'] = result
            return redirect('/success')
    return redirect('/')

@app.route("/login-user", methods=["POST"])
def login_user():
    isValid = True

    if not EMAIL_REGEX.match(request.form['email']):   
        isValid = False
        flash("Invalid email address!")
    
    if isValid:
        mysql = connectToMySQL("basic_registration")
        data ={
        'email': request.form['email'],
        'psw': request.form['password'] 
        }   
        query = "SELECT * FROM users WHERE email = %(email)s;"
        result = mysql.query_db(query, data)
        if result:
            if bcrypt.check_password_hash(result[0]['password'], request.form['password']):
                session['userid'] = result[0]['id']
                return redirect('/success')
        flash("Could not login")
        return redirect("/")
@app.route("/success", methods =["GET"])
def welcome_user():

    if 'userid' in session:
        mysql = connectToMySQL("basic_registration")
        query = "SELECT * FROM users WHERE id = %(user)s;"
        query2 = "SELECT * FROM tweets inner join users on tweets.user_id = users.id"
        data ={
        'user': session['userid']
        }  
        result = mysql.query_db(query,data)
        mysql = connectToMySQL("basic_registration")
        result2 = mysql.query_db(query2)
        print(result2)
        if result:
            user = result[0]
            print(user)
        return render_template('success.html', user = user, tweets = result2)
    else:
        flash("Session timeout")
        return redirect('/')
@app.route('/logout', methods=["GET"])
def logout_user():
    session.clear()
    return redirect('/')

@app.route('/tweets/create', methods=["POST"])
def create_tweet():
    is_valid = True
    if len(request.form['tweet']) < 1 or len(request.form['tweet'])>255:
        is_valid = False
        flash("Tweet needs to be between 1 and 255")
    if is_valid:
        flash("Succesfully tweeted!")
        mysql = connectToMySQL("basic_registration")
        data ={
            'tweet': request.form['tweet'],
            'user_id': session['userid']
        }
        query = "INSERT INTO tweets(tweet, user_id) VALUES(%(tweet)s, %(user_id)s);"
        result = mysql.query_db(query, data)
        return redirect('/success')

    return redirect('/')



if __name__== "__main__":
    app.run(debug=True)