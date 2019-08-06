from flask import Flask, session, url_for, redirect, escape,render_template, request,abort
from hashlib import md5
import os
import pymysql
#from flaskext.mysql import MySQL
app = Flask(__name__)
# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app
# Connect to the database
def create_connection():
    return pymysql.connect(host='localhost',
                             user='root',
                             password='13COM',
                             db='students1',
                             charset='utf8mb4'
                             ,cursorclass=pymysql.cursors.DictCursor)





def display_all_records(username,role="admin",Id=0):
    global data
    connection=create_connection()
    try:
        with connection.cursor() as cursor:
          #pull records and display using a left join
          #select_sql = "SELECT * from users"
          #if role not "admin"
          select_sql = "SELECT users.Id As Id,users.Email AS Email,users.FirstName AS FirstName, users.FamilyName As FamilyName,profiles.DateOfBirth As DateOfBirth,profiles.Photo as Photo FROM users LEFT JOIN profiles ON users.Id=profiles.UserId"
          if int(Id)>0:
            print(select_sql)
            print (Id)
            select_sql = select_sql+" Where users.Id="+Id
            val=(int(Id))
            print(select_sql)
            cursor.execute(select_sql)
            data = cursor.fetchone()
            print(data)
          cursor.execute(select_sql)
          data = cursor.fetchall()
          data=list(data)
    finally:
          connection.close()
# allowed image
def allowed_image(filename):
    if not "." in filename:
        return False
    ext = filename.rsplit(".", 1)[1]
    if ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return True
    else:
        return False

app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["JPEG", "JPG", "PNG", "GIF"]
upload_folder = os.getcwd() + "/static/images"
app.config['upload_folder'] = upload_folder

class ServerError(Exception):pass

#login
@app.route('/login', methods=['GET', 'POST'])
def login():
    connection=create_connection()
    if  session.get('logged_in'):
        display_all_records()
        username_session=escape(session['username']).capitalize()
        return redirect(url_for("index", results=data,session_user_name=username_session))
    error = None
    try:
        with connection.cursor() as cursor:
         if request.method == 'POST':
            username_form  = request.form['username']
            select_sql = "SELECT COUNT(1) FROM users WHERE Username = %s"
            val =(username_form)
            cursor.execute(select_sql,val)
            #data = cursor.fetchall()

            if not list(cursor.fetchone())[0]:
                raise ServerError('Invalid username')

            password_form  = request.form['password']
            select_sql = "SELECT Password from users WHERE Username = %s"
            val=(username_form)
            cursor.execute(select_sql,val)
            data = list(cursor.fetchall())
            #print (data)
            for row in data:
                #print(md5(password_form.encode()).hexdigest())
                if md5(password_form.encode()).hexdigest()==row['Password']:
                    session['username'] = request.form['username']
                    session['logged_in'] = True
                    return redirect(url_for('home'))

            raise ServerError('Invalid password')
    except ServerError as e:
        error = str(e)
        session['logged_in']=False

    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

#display users
@app.route('/')
def home():
	if session.get('logged_in'):
		username_session=escape(session['username']).capitalize()
		return render_template("index.html",session_user_name=username_session)
	
	username_session=""
	return render_template("index.html")
    #try:
    #    with connection.cursor() as cursor:
    #        sql = "SELECT * from users"
    #        cursor.execute(sql)
    #        data = cursor.fetchall()
    #        data=list(data)
    #finally:
    #        connection.close()

@app.route('/users')
def users():
	if session.get('logged_in'):
		username_session=escape(session['username']).capitalize()
		display_all_records(username_session ,role="admin")
		return render_template("index.html",session_user_name=username_session,results=data)
	username_session=""
	return redirect(url_for('login'))
    #try:
    #    with connection.cursor() as cursor:
    #        sql = "SELECT * from users"
    #        cursor.execute(sql)
    #        data = cursor.fetchall()
    #        data=list(data)
    #finally:
    #        connection.close()



# update from form
@app.route('/add_user', methods=['POST','GET'])
def new_user():
	connection=create_connection()
	try:
		with connection.cursor() as cursor:
		#pull records and display
			sql = "SELECT * from roles"
			cursor.execute(sql)
			roles = cursor.fetchall()
			roles=roles
	finally:
		connection.close()
		if request.method == 'POST':
			form_values = request.form 
			first_name = form_values["firstname"]
			family_name = form_values["familyname"]
			username = form_values["username"]
			email = form_values["email"]
			password = form_values["password"]
			role = form_values['role']
			dob="2001-10-01"
		try:
			with connection.cursor() as cursor:
				# Create a new record
				sql = "INSERT INTO `users` (FirstName,FamilyName,Email,DateOfBirth,Password,UserName, roles) VALUES (%s,%s,%s,%s,%s,%s,%s)"
				val=(first_name,family_name,email,dob,password,username,role)
				cursor.execute(sql,(val))
				#save values in dbase
			connection.commit()
			cursor.close()
			with connection.cursor() as cursor:
				#pull records and display
				sql = "SELECT * from users"
				cursor.execute(sql)
				data = cursor.fetchall()
				data=list(data)
		finally:
			connection.close()
		return redirect(url_for('home'))
	return render_template("add_user.html", roles=roles)



# Tasks 
# Per assessment AS91902 Document; complex techniques  include creating queries which insert, update or delete to modify data
# so you should add  new routes for edit_user, user_details and delete_user using record ids
# create the html pages needed
# modify database to include an image field which will store the image filename(eg pic.jpg) in database and  implement this functionality in code where applicable
if __name__ == '__main__':
	import os
	app.secret_key = os.urandom(12)   
	class ServerError(Exception):pass
	HOST = os.environ.get('SERVER_HOST', 'localhost')
	try:
		PORT = int(os.environ.get('SERVER_PORT', '5555'))
	except ValueError:
			PORT = 5555
	app.run(HOST, PORT)