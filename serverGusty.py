import psycopg2
import psycopg2.extras

from flask import Flask, render_template, request, redirect, url_for
from flask import session
import os

app = Flask(__name__)
app.secret_key = os.urandom(24).encode('hex')

# Original design used global variables, but since a web-site can have many
# users at one time, globals do not work.
# You need session variables, which flask provides for you in the session dict
# I retained the global variables, which track that last person to login
currentUser = ''
zipCode = ''
#session['username'] = '' -- cant reference session here

def connectToDBSession():
  connectionString = 'dbname=session user=gusty password= host=localhost'
  try:
    return psycopg2.connect(connectionString)
  except:
    print("Can't connect to database")


@app.route('/', methods=['GET', 'POST'])
def mainIndex():
    if 'username' in session:
      localCurrentUser = session['username']
    else:
      localCurrentUser = ''
      
    db = connectToDBSession()
    cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    queryType = 'None'
    print('User: ' + currentUser) #session['username'])
    rows = []
    # if user typed in a post ...
    print("Current user", 'username' in session)
    if request.method == 'POST':
      searchTerm = request.form['search']
      if searchTerm == 'movies':
         #if currentUser != '':
         if 'username' in session:
            localCurrentUser = session['username']
            zipCode = session['zipCode']
            query = cur.mogrify("""SELECT * FROM movies WHERE zip=%s;""",(zipCode,))
            print("mogrify-movies", query)
         else:
            query = "SELECT * from movies"
         queryType = 'movies'
      else:
         #if currentUser != '':
         if 'username' in session:
            localCurrentUser = session['username']
            zipCode = session['zipCode']
            query = cur.mogrify("""SELECT * FROM stores where (name LIKE %s OR type LIKE %s) and zip='%s' ORDER BY name""", ('%'+searchTerm+'%', '%'+searchTerm+'%', zipCode))
            print("mogrify-else",query)
         else:
            query = cur.mogrify("""SELECT * FROM stores where name LIKE %s OR type LIKE %s ORDER BY name""", ('%'+searchTerm+'%', '%'+searchTerm+'%'))
         queryType = 'stores'
      print ("query before cur.execute()", query)
      cur.execute(query)
      rows = cur.fetchall()
      

    return render_template('index.html', queryType=queryType, results=rows, selectedMenu='Home',currentUser=localCurrentUser)

@app.route('/login', methods=['GET', 'POST'])
def login():
    invalidAccountCreation = "False"
    global currentUser, zipCode
    localCurrentUser = ''
    db = connectToDBSession()
    cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    # if user typed in a post ...
    if request.method == 'POST':
      if 'submit' in request.form:
        print "testing submit"
        print "HI"
        username = request.form['username']
        currentUser = username
        localCurrentUser = username

        pw = request.form['pw']
        session['username'] = username
        if username == 'ann' or username == 'raz' or username == 'lazy':
          query = cur.mogrify("""SELECT * FROM users WHERE username = %s AND password = %s""", (username, pw))
          #query = "select * from users WHERE username = '%s' AND password = '%s'" % (username, pw)
        else:
          query = cur.mogrify("""SELECT * FROM users WHERE username = %s AND password = crypt(%s,password)""", (username, pw))

        print query
        print request.form['submit']
        cur.execute(query)
        fetchOne = cur.fetchone()
        print "Gusty", fetchOne
        #for record in cur:
           #print record
        if fetchOne:
           zipCode = fetchOne[3]
           session['zipCode'] = fetchOne[3]
           print "here fetchone"
           print "GustyIf", fetchOne, zipCode, type(zipCode)
           return redirect(url_for('mainIndex'))
        else:
           currentUser = ''
           localCurrentUser = ''
           zipCode = ''

      if 'createAccount' in request.form:
        print "testing createAcount"
        username = request.form['username']
        currentUser = username
        localCurrentUser = username
        pw = request.form['pw']
        zipCode = request.form['zipCode']
        if username != '' and pw != '' and zipCode != '':
          # could put some rules on username, pw, and zipCode here
          # Should also put logic in to make sure account does not already exist
          zipCode = int(zipCode)
          query = cur.mogrify("""INSERT INTO users (username,password,zipcode) VALUES (%s,crypt(%s,gen_salt('bf')),%s)""", (username, pw,zipCode))
          
          print query
          cur.execute(query)
          print(cur.statusmessage)
          db.commit()
          session['username'] = username
          session['zipCode'] = zipCode
        else:
          invalidAccountCreation = "True"
    return render_template('login.html', selectedMenu='Login',currentUser=localCurrentUser,invalidAccountCreation=invalidAccountCreation)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    global currentUser, zipCode
    print 'LOGOUT'
    localCurrentUser = session['username']
    if request.method == 'POST':
      print "Logout1"
      if 'logout' in request.form:
        print("submit",request.form['logout'])
        session.pop('username', None)
        session.pop('zipCode', None)
        currentUser = ''
        zipCode = ''
        return redirect(url_for('mainIndex'))
      if 'doNotLogout' in request.form:
        return redirect(url_for('mainIndex'))
    return render_template('logout.html', selectedMenu='Logout',currentUser=localCurrentUser)

if __name__ == '__main__':
    app.debug=True
    app.run(host='0.0.0.0', port=8080)
