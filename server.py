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
        mysql = connectToMySQL("dojo_tweets")
        pw_hash = bcrypt.generate_password_hash(request.form['password'])  
        data ={
            'fn': request.form['firstName'],
            'ln': request.form['lastName'],
            'em': request.form['email'],
            'psw': pw_hash
        }
        
        query = "INSERT INTO users(fname, lname, email,password) VALUES(%(fn)s, %(ln)s,%(em)s, %(psw)s);"
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
        mysql = connectToMySQL("dojo_tweets")
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
        mysql = connectToMySQL("dojo_tweets")
        query = "SELECT * FROM users WHERE id = %(user)s;"
        query2 = "SELECT * FROM tweets inner join users on tweets.users_id = users.id"

        data ={
        'user': session['userid']
        }  
        result = mysql.query_db(query,data)
        mysql = connectToMySQL("dojo_tweets")
        result2 = mysql.query_db(query2)
        mysql = connectToMySQL("dojo_tweets")


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
        mysql = connectToMySQL("dojo_tweets")
        data ={
            'tweet': request.form['tweet'],
            'user_id': session['userid']
        }
        query = "INSERT INTO tweets(content, users_id) VALUES(%(tweet)s, %(user_id)s);"
        result = mysql.query_db(query, data)
        return redirect('/success')

    return redirect('/')


@app.route('/tweets/<tweet_id>/add_like')
def like_tweet(tweet_id):
    print(tweet_id)
    mysql = connectToMySQL("dojo_tweets")
    query = "INSERT INTO liked_tweets(tweets_id, users_id) VALUES(%(tweet_id)s, %(user_id)s);"
    data ={
        'tweet_id': tweet_id,
        'user_id': session['userid']
        }
    result = mysql.query_db(query, data)
    return redirect('/success')


@app.route('/tweets/<tweet_id>/delete')
def delete_tweet(tweet_id):
    print(tweet_id)
    mysql = connectToMySQL("dojo_tweets")
    query = "DELETE FROM liked_tweets where liked_tweets.tweets_id = %(tweet_id)s;"
    query2 = "DELETE FROM tweets where tweets.id = %(tweet_id)s;"
    data ={
        'tweet_id': tweet_id
        }
    mysql.query_db(query, data)
    mysql = connectToMySQL("dojo_tweets")
    mysql.query_db(query2, data)
    
    return redirect('/success')


@app.route('/tweets/<tweet_id>/edit')
def render_edit_tweet(tweet_id):
    print(tweet_id)
    mysql = connectToMySQL("dojo_tweets")
    query = "SELECT * FROM tweets where tweets.id =%(tweet_id)s;"
    data ={
        'tweet_id': tweet_id
    }
    result = mysql.query_db(query, data)


    return render_template('edit_tweet.html', tweet = result[0])


@app.route('/tweets/<tweet_id>/update', methods=["POST"])
def update_tweet(tweet_id):
    is_valid = True
    if len(request.form['tweet']) < 1 or len(request.form['tweet'])>255:
        is_valid = False
        flash("Tweet needs to be between 1 and 255")
    if is_valid:
        flash("Succesfully tweeted!")
        mysql = connectToMySQL("dojo_tweets")
        data ={
            'tweet': request.form['tweet'],
            'user_id': session['userid']
        }
        query = "UPDATE tweets set tweets.content =%(tweet)s where tweets.users_id =  %(user_id)s;"
        result = mysql.query_db(query, data)
        return redirect('/success')

    return redirect(f'/tweets/{tweet_id}/edit')





if __name__== "__main__":
    app.run(debug=True)