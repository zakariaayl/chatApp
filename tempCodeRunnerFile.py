from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_socketio import SocketIO, send, join_room, leave_room, emit
from sqlalchemy import select, desc
from models import User, db, Message
import ssl
from email.message import EmailMessage
import smtplib
import config
import secrets
import datetime
import base64

app = Flask(__name__)
app.config.from_object(config)
socketio = SocketIO(app)
db.init_app(app)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

user_sessions = {}

# Page Home with a Nav bar and description of the Chat App
@app.route('/', methods=["GET", "POST"])
def home():
    if request.method == "POST":
        action = request.form.get('action')
        if action == "login":
            return redirect(url_for("login"))
        elif action == "register":
            return redirect(url_for("register"))
        else:
            return render_template("home.html")
    else:
        return render_template("home.html")




# User login
@app.route('/login', methods=["GET", "POST"])
def login():
 if 'message'not in session:
    if request.method == "POST":
        action = request.form.get('action')
        if action == "login":
            username = request.form.get('username')
            password = request.form.get('password')
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password) and user.Is_actif():
                session["username"] = username
                return redirect(url_for("fetch_users"))
            else:
                return render_template("login.html", message="Invalid username or password")
        else:
            return redirect(url_for("register"))
    else:
        return render_template("login.html")
 else:
    message=session.get('message')
    del session['message']
    return render_template("login.html",message=message)

# User registration
@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        FirstName = request.form.get('firstname')
        LastName = request.form.get('lastname')
        username = request.form.get('username')
        email = request.form.get('mail')
        session['email'] = email
        password = request.form.get('password')
        # Handle registration
        errors = []
        if not email or User.query.filter_by(email=email).first():
            errors.append("Email is empty or not valid, or is already entered by another user.")
        if not FirstName or len(FirstName) < 3:
            errors.append("First name is empty or not valid.")
        if not LastName or len(LastName) < 3:
            errors.append("Last name is empty or not valid.")
        if not username or len(username) < 3:
            errors.append("Username is empty or not valid.")
        if not password or len(password) < 3:
            errors.append("Password is empty or not valid.")
        if errors:
            return render_template("register.html", message=" ".join(errors))
        
        if not User.query.filter_by(username=username).first():
            #verify(email)
            new_user = User(username=username)
            new_user.email = email.lower()
            new_user.FirstName = FirstName.capitalize()
            new_user.LastName = LastName.upper()
            new_user.set_password(password)
            new_user.actif = True
            db.session.add(new_user)
            db.session.commit()
            session["username"] = username
            return redirect(url_for("conf", var='N'))
        else:
            return render_template("register.html", message="Username already exists")
    else:
        return render_template("register.html")


@app.route('/update_profile', methods=['GET', 'POST'])
def update_profile():
    if 'username' not in session:
        return redirect(url_for('login'))

    user = User.query.filter_by(username=session.get('username')).first()

    if request.method == 'POST':
        action = request.form['action']
        if action == 'update':
            try:
                Users=User.query.all()
                test_exist=True
                for us in Users:
                  if (us.username).lower()==request.form['username'].lower():
                    test_exist=False
                if test_exist:
                    user.FirstName = request.form['first_name'] 
                    user.LastName = request.form['last_name']
                    user.username = request.form['username']
                    if request.form['password']:
                        user.set_password(request.form['password'])
                    db.session.commit()
                    session['username'] = user.username
                    return render_template("update_profile.html", user=user, message="Profile updated successfully!")
            except Exception as e:
                db.session.rollback()
                return render_template("update_profile.html", user=user, message=f"Error updating profile: {str(e)}")
        elif action == 'annuler':
            return redirect(url_for("chat",name=session.get('username')))
    else:
        return render_template('update_profile.html', user=user)
# Chat functionality
@app.route('/chat/<name>', methods=["GET", "POST"])
def chat(name):
    if request.method == "POST":
        action = request.form.get('action')
        if action == 'account':
            return  redirect(url_for("update_profile"))
        elif action == 'deconnexion':
            del session['username']
            session['message']="vous ête déconnecter!!"
            return redirect(url_for("login"))
    
    if "username" not in session:
        return redirect(url_for('login'))
    
    if not name:
        return redirect(url_for('fetch_users'))
    
    if session.get('username') == name:
        return redirect(url_for('fetch_users'))
    
    session['name'] = name
    username = session["username"]
    messages = Message.query.filter(
        ((Message.sender == username) & (Message.recipient == name)) |
        ((Message.sender == name) & (Message.recipient == username))
    ).order_by(Message.timestamp).all()
    
    users = User.query.all()
    user_list = [{"name": user.username} for user in users if user.username != session.get('username')]
    messages_list = [{"sender": message.sender, "recipient": message.recipient, "timestamp": message.timestamp, "content": message.content, "img": message.img, "pdf": message.pdf} for message in messages]

    return render_template('chat.html', username=username, messages=messages_list, users=user_list, reciver=name)



@app.route('/users', methods=['GET','POST'])
def fetch_users():
    if not request.method=='POST':
        users = User.query.all()
        user_list = [{'name': user.username} for user in users if user.username != session.get('username')]
        return render_template('fetch_user.html', users=user_list,username=session.get('username'))
    else:
        action = request.form.get('action')
        if action == 'account':
            return  redirect(url_for("update_profile"))
        elif action == 'deconnexion':
            session['message']="vous ête déconnecter"
            del session['username']
            return redirect(url_for("login",))
        


@app.route('/conf/<var>')
def conf(var):
    if "username" in session:
        if var == 'Y':
            verify(session.get('email'))
            return redirect(url_for('conf', var='N'))
        else:
            return render_template('conf.html', username=session["username"])

@app.route('/confirm/<token>')
def confirm_email(token):
    email = decode_token(token)
    if email:
        user = User.query.filter_by(email=email).first()
        if user:
            flash("Your email is validated. Enter your username and password and enjoy our app.")
            user.actif = True
            db.session.commit()
            return redirect(url_for('login'))
        else:
            return "Invalid token or user does not exist", 400
    else:
        return "Invalid token", 400


@socketio.on('connect')
def handle_connect():
    username = session.get('username')
    if username:
        user_sessions[username] = request.sid
        join_room(username)

@socketio.on('disconnect')
def handle_disconnect():
    username = session.get('username')
    if username in user_sessions:
        leave_room(username)
        del user_sessions[username]

@socketio.on('message')
def handle_message(data):
    sender = session.get('username')
    recipient = session.get('name')
    msg = data.get('message')

    new_message = Message(content=msg, sender=sender, recipient=recipient)
    db.session.add(new_message)
    db.session.commit()

    timestamp = new_message.timestamp.strftime('%H:%M')
    date = new_message.timestamp.strftime('%d %B')

    message_data = {
        'message': msg,
        'sender': sender,
        'timestamp': timestamp,
        'date': date
    }

    send(message_data, room=sender)
    send(message_data, room=recipient)
    print(f"Message from {sender} to {recipient}: {msg} at {timestamp} on {date}")

@socketio.on('join')
def on_join(data):
    username = session.get('username')
    room = data['room']
    join_room(room)
    user_sessions[username] = request.sid
    message = f"{username} is online."
    print(message)
    emit('user_joined', {'msg': message}, room=room)

@socketio.on('image')
def handle_image(data):
    username = data['username']
    img = data['img']
    recipient = session.get('name')

    if recipient:
        try:
            message = Message(img=img, content='', sender=username, recipient=recipient)
            db.session.add(message)
            db.session.commit()
            
            timestamp = message.timestamp.strftime('%H:%M')
            date = message.timestamp.strftime('%d %B')
            emit('image', {'sender': username, 'img': img, 'timestamp': timestamp, 'date': date}, room=recipient)
            emit('image', {'sender': username, 'img': img, 'timestamp': timestamp, 'date': date}, room=username)
            print(f"Image sent from {username} to {recipient}")
        except Exception as e:
            print(f"Error saving image: {e}") 

@socketio.on('pdf')
def handle_pdf(data):
    username = data['username']
    pdf = data['pdf']
    recipient = session.get('name')

    if recipient:
        try:
            message = Message(pdf=pdf, content='', sender=username, recipient=recipient)
            db.session.add(message)
            db.session.commit()
            
            timestamp = message.timestamp.strftime('%H:%M')
            date = message.timestamp.strftime('%d %B')
            emit('pdf', {'sender': username, 'pdf': pdf, 'timestamp': timestamp, 'date': date}, room=recipient)
            emit('pdf', {'sender': username, 'pdf': pdf, 'timestamp': timestamp, 'date': date}, room=username)
            print(f"PDF sent from {username} to {recipient}")
        except Exception as e:
            print(f"Error saving PDF: {e}")

def verify(email):
    em = EmailMessage()
    em['From'] = 'ayougilzakaria@gmail.com'
    email_pass = 'your-email-password'
    em['To'] = email
    session['email'] = em['To']
    token = generate_token(em['To'])
    em['Subject'] = 'Verify your account'
    body = f'Congrats you are now registered in our chat app. Please verify your email by clicking on http://127.0.0.1/confirm/{token}'
    em.set_content(body)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', context=context) as smtp:
        smtp.login(em['From'], email_pass)
        smtp.sendmail(em['From'], em['To'], em.as_string())

def generate_token(email):
    token = secrets.token_urlsafe()
    combined = f"{email}:{token}"
    encoded = base64.urlsafe_b64encode(combined.encode()).decode()
    return encoded

def decode_token(token):
    try:
        decoded = base64.urlsafe_b64decode(token.encode()).decode()
        email, token_value = decoded.split(':')
        return email
    except Exception as e:
        return None



if __name__ == '__main__':
    app.secret_key = 'my key'
    socketio.run(app, host="0.0.0.0", debug=True)
