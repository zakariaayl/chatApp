from gevent import monkey # type: ignore
monkey.patch_all()
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_socketio import SocketIO, send, join_room, leave_room, emit
from sqlalchemy import select, desc,or_, and_
from models import User, db, Message,Friendship
import ssl
from email.message import EmailMessage
import smtplib
import config
import secrets
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import base64
from io import BytesIO
from deep_translator import GoogleTranslator
import time
from mtranslate import translate
import logging
import string
import random
import re
from flask_cors import CORS








app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
app.config.from_object(config)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
logging.basicConfig(level=logging.INFO)
socketio = SocketIO(app, logger=True,async_mode='gevent', engineio_logger=True)
db.init_app(app)


user_sessions = {}



# Error handler for 400 Bad Request
@app.errorhandler(400)
def bad_request_error(error):
    return redirect(url_for('home', error='400'))

# Error handler for 404 Not Found
@app.errorhandler(404)
def not_found_error(error):
    return redirect(url_for('home', error='404'))

# Error handler for 500 Internal Server Error
@app.errorhandler(500)
def internal_server_error(error):
    return redirect(url_for('home', error='500'))




# Page Home with a Nav bar and description of the Chat App
@app.route('/', methods=["GET", "POST"])
def home():
    if request.method == "POST":
        action = request.form.get('action')
        if action == "login":
            return redirect(url_for("login",var='N'))
        elif action == "register":
            return redirect(url_for("register"))
        else:
            return render_template("home.html")
    else:
        return render_template("home.html")




# User login
@app.route('/login/<var>', methods=["GET", "POST"])
def login(var):
 if var=='Y':
     email=session['email']
     verify(email,'email.html',0)
     return redirect(url_for("login",var='N'))
 else :
    if 'message'not in session and 'msg' not in session:
            if request.method == "POST":
                action = request.form.get('action')
                if action == "login":
                    username = request.form.get('username')
                    password = request.form.get('password')
                    user = User.query.filter_by(username=username).first()
                    if user and user.check_password(password) and user.actif:
                        session["username"] = username
                        return redirect(url_for("fetch_users"))
                    elif user and user.check_password(password) and not user.actif:
                        
                        return render_template("login.html", message="you're email is not actif check your email to activate you're account",pop="1")
                    else:
                        return render_template("login.html", message="Invalid username or password")
                else:
                    return redirect(url_for("register"))
            else:
                return render_template("login.html")
    else:
            
            
            if 'msg' in session and 'message' in session:
                msg = session.get('msg')
                del session['msg']
                message=session.get('message')
                del session['message']
            # print(msg)
            
            
                return render_template("login.html",message=message,msg=msg)
            
            if 'message' in session:
                   message=session.get('message')
                   del session['message']
                   return render_template("login.html",message=message)
            if 'msg' in session:
                   msg=session.get('msg')
                   del session['msg']
                   return render_template("login.html",msg=msg)
            return render_template("login.html")

# User registration
@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
     action=request.form.get('action')
     if action=='inscrire':
        FirstName = request.form.get('firstname')
        LastName = request.form.get('lastname')
        username = request.form.get('username')
        email = request.form.get('mail')
        session['email'] = email
        password = request.form.get('password')
        image = request.files.get('file')
        lang=request.form.get('lg')
        if(lang=='default'):
            session['lalguage']=False
            lang='en'
        # session['lg1']=lang
        errors = []
        if  image:
        
            try:
                    image_stream = BytesIO(image.read())
                    image_base64 = base64.b64encode(image_stream.getvalue()).decode('utf-8')
            except Exception as e:
                errors.append(f"Error processing image: {str(e)}")
        
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
            verify(email,'email.html',0)
            new_user = User(username=username)
            new_user.email = email.lower()
            new_user.FirstName = FirstName.capitalize()
            new_user.LastName = LastName.upper()
            new_user.set_password(password)
            new_user.actif = False
            if image:
             new_user.img=image_base64
            new_user.lang=lang
            db.session.add(new_user)
            db.session.commit()
            session["username"] = username
            session['msg']="you re registration is almost done,please check in your email for validate your account if there is no mail click on"
            
            return redirect(url_for("login",var='N'))

        else:
            return render_template("register.html", message="Username already exists")
     elif action=='login':
        return redirect(url_for("login",var="N"))
     
    else:
        return render_template("register.html")

@app.route('/forgot', methods=["GET", "POST"])
def forgot():
    user=request.form.get('user')
    user_db=User.query.filter_by(username=user).first()
    # print(user_db)
    if user_db :
        s1 = list(string.ascii_lowercase)
        s2 = list(string.ascii_uppercase)
        s3 = list(string.digits)
        s4 = list(string.punctuation)
        random.shuffle(s1)
        random.shuffle(s2)
        random.shuffle(s3)
        random.shuffle(s4)
        part1 = round(10 * (30/100))
        part2 = round(10 * (20/100))
        result = []
        for x in range(part1):
        
            result.append(s1[x])
            result.append(s2[x])
        for x in range(part2):
        
            result.append(s3[x])
            result.append(s4[x])
        random.shuffle(result)
        password = "".join(result)
        print("Strong Password: ", password)
        user_db.set_password(password)
        db.session.commit()
        verify(user_db.email,'pass.html',password)
        print('the email is send succesifuly')
        return render_template('forgot.html',message="the email is send succesifuly")
    else:
        print('the username is not in the database')
        return render_template('forgot.html',message="the username is not in the database")
    return render_template('forgot.html')

@app.route('/update_profile', methods=['GET', 'POST'])
def update_profile():
    if 'username' not in session:
        return redirect(url_for('login',var='N'))

    user = User.query.filter_by(username=session.get('username')).first()

    if request.method == 'POST':
        action = request.form['action']
        if action == 'update':
            try:
                # Check if the username already exists
                existing_user = User.query.filter_by(username=request.form.get('username')).first()
                if existing_user and existing_user.username != user.username:
                    return render_template("update_profile.html", user=user, message="Username already taken.")
                user.FirstName = request.form.get('first_name')
                user.LastName = request.form.get('last_name')
                
                if request.form.get('password'):
                    user.set_password(request.form.get('password'))

                image = request.files.get('file')
                print(image)
                print(".............")
                if  image:
                         image_stream = BytesIO(image.read())
                         image_base64 = base64.b64encode(image_stream.getvalue()).decode('utf-8')
                         print(image_base64)
                         user.img=image_base64
                db.session.commit()
                return render_template("update_profile.html", user=user, message="Profile updated successfully!")
                
            except Exception as e:
                db.session.rollback()
                return render_template("update_profile.html", user=user, message=f"Error updating profile: {str(e)}")
        else:
            return redirect(url_for("chat", name=session.get('username')))
    
    return render_template('update_profile.html', user=user)
    
# Chat functionality
@app.route('/chat/<name>', methods=["GET", "POST"])
def chat(name):
    session["back"] = "chat"
    if request.method == "POST":
        action = request.form.get('action')
        if action == 'account':
            return redirect(url_for("update_profile"))
        elif action == 'deconnexion':
            del session['username']
            session['message'] = "vous ête déconnecter!!"
            return redirect(url_for("login", var='N'))
        elif action == 'notif':
            return redirect(url_for("notif"))

    if "username" not in session:
        return redirect(url_for('login', var='N'))

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

    friends = db.session.query(User).join(Friendship, or_(
            and_(Friendship.friend == User.username, Friendship.user == username),
            and_(Friendship.user == User.username, Friendship.friend == username)
        )
    ).filter(Friendship.accepted == True).all()

    friend_list = [{"name": user.username, "lang": user.lang, "img": user.img} for user in friends if user.username != session.get('username')]
    user = User.query.filter_by(username=session.get('username')).first()
    
    lang_update = request.form.get('lg')
    if lang_update:
        user.lang = lang_update
        db.session.commit()

    user_2 = User.query.filter_by(username=name).first()
    lg2 = user_2.lang
    session['lg2'] = lg2
    lg1 = User.query.filter_by(username=session.get('username')).first().lang
    session['lg1'] = lg1

    start_time = time.time()
    contents = [message.content for message in messages]
    unique_delimiter = "<-mg->"
    y = unique_delimiter.join(contents)
    
   
    y = y.replace("*", "")

    print(y)  
    if lg1 == lg2:
        contents_trans = GoogleTranslator(source='th', target=lg1).translate(y)
    else:
        contents_trans = GoogleTranslator(source=lg2, target=lg1).translate(y)

    print(contents_trans)  
    
    print(".............kifach ja")

    contents_trans = re.sub(r'\s*<\s*-\s*mg\s*->\s*', '<-mg->', contents_trans)

    contents_trans = re.sub(r'(<-mg->)+', lambda m: m.group(0).replace("<-mg->", "<-mg->*"), contents_trans)

    t = contents_trans.split(unique_delimiter)

    if len(messages) == 0:
        t = ""

    print(f"Number messages: {len(messages)}")
    print(f"Number of t: {len(t)}")
    print("...........messages")
    print(messages)
    print(".............t li mfer9a")
    print(t)
    print(".............content_trans_khassykon_nady")
    print(contents_trans)
    print(".............")

   
    if len(messages) != len(t):
        t.extend([""] * (len(messages) - len(t)))
        print("Mismatch detected between original and translated messages.")

    
    messages_list = [
        {
            "sender": message.sender,
            "recipient": message.recipient,
            "timestamp": message.timestamp,
            "content": t[i].replace("*", ""),  
            "img": message.img,
            "pdf": message.pdf
        } for i, message in enumerate(messages)
    ]

    end_time = time.time()
    print(f"Translation Time: {end_time - start_time} seconds")

    user_img_data = None
    if user_2.img:
        user2_img_data = f"data:image/png;base64,{user_2.img}"
    user_img = User.query.filter_by(username=session.get('username')).first().img
        
    if user_img:
        user_img_data = f"data:image/png;base64,{user_img}"
        if user_2.img:
            return render_template('chat.html', username=username, messages=messages_list, users=friend_list, reciver=name, user2=user2_img_data, user=user_img_data)
        else:
            return render_template('chat.html', username=username, messages=messages_list, users=friend_list, reciver=name, user=user_img_data)
    else:
        if user_2.img:
            return render_template('chat.html', username=username, messages=messages_list, users=friend_list, reciver=name, user2=user2_img_data)
        else:
            return render_template('chat.html', username=username, messages=messages_list, users=friend_list, reciver=name)





@app.route('/users', methods=['GET', 'POST'])
def fetch_users():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'account':
            return redirect(url_for("update_profile"))
        elif action == 'deconnexion':
            session['message'] = "vous êtes déconnecté"
            del session['username']
            return redirect(url_for("login",var='N'))
        elif action=='notif':
            return redirect(url_for("notif"))
    elif request.method == 'GET':
        action = request.args.get('action')
        username = request.args.get('username')
        current_user = session.get('username')

        if action == 'add' and username and current_user:
            existing_friendship = Friendship.query.filter(
                ((Friendship.user == current_user) & (Friendship.friend == username)) |
                ((Friendship.user == username) & (Friendship.friend == current_user))
            ).first()

            if existing_friendship:
                flash(f'Friend request to {username} already exists.')
                return redirect(url_for('fetch_users'))
            else:
                new_friendship = Friendship(user=current_user, friend=username, accepted=False)
                db.session.add(new_friendship)
                db.session.commit()
                flash(f'Friend request sent to {username}')
                socketio.emit('friend_request', {'from': current_user, 'to': username}, room=username)
                return redirect(url_for('fetch_users'))

        elif action == 'delete' and username and current_user:
            existing_friendship = Friendship.query.filter(
                ((Friendship.user == current_user) & (Friendship.friend == username)) |
                ((Friendship.user == username) & (Friendship.friend == current_user))
            ).first()

            if existing_friendship:
                db.session.delete(existing_friendship)
                db.session.commit()
                flash(f'Friendship with {username} has been deleted.')
                
            else:
                flash(f'No friendship exists with {username}.')
            return redirect(url_for('fetch_users'))

        users = User.query.all()
        friends = Friendship.query.filter(((Friendship.user == current_user) | (Friendship.friend == current_user))).all()
        user_list = [{'name': user.username} for user in users if user.username != current_user]
        friends_list = [{'name': friend.user if friend.user != current_user else friend.friend} for friend in friends if friend.accepted==True]
        request_list=[{'name': request.user if request.user!=current_user else request.friend} for request in friends]
        return render_template('fetch_user.html', users=user_list, friends=friends_list, username=current_user,requests=request_list)
@app.route('/notif', methods=['GET', 'POST'])
def notif():
    if request.method=="POST":
        action=request.form.get('action')
        if action=="account":
            return redirect(url_for("update_profile"))
        elif action=="deconnexion":
            del session["username"]
            session
            return redirect(url_for("login",var='N'))
    if request.method == 'GET':
        action = request.args.get('action')
        username = request.args.get('username')
        current_user = session.get('username')
        
        if action and username and current_user:
            if action == 'add':
                req = Friendship.query.filter(
                    ((Friendship.user == username) & (Friendship.friend == current_user)) |
                    ((Friendship.user == current_user) & (Friendship.friend == username))).first()
                
                if req:
                    req.accepted = True
                    db.session.commit()
                    flash('Request accepted')
                    return redirect(url_for('notif'))
            
            elif action == 'delete':
                existing_friendship = Friendship.query.filter(
                    ((Friendship.user == current_user) & (Friendship.friend == username)) |
                    ((Friendship.user == username) & (Friendship.friend == current_user))
                ).first()
                
                if existing_friendship:
                    db.session.delete(existing_friendship)
                    db.session.commit()
                    flash(f'Request from {username} has been deleted.')
                    return redirect(url_for('notif'))

    user_requests = Friendship.query.filter(
     (Friendship.friend == session.get('username')) & (Friendship.accepted == False)).all()

    requests = [{'name': user.user} for user in user_requests]
    
    return render_template("notif.html", users=requests,username=session.get('username'))


@app.route('/conf/<var>')
def conf(var):
    if "username" in session:
        if var == 'Y':
            verify(session.get('email'),'email.html',0)
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
            return redirect(url_for('login',var='N'))
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
    try:
    # Existing code for message handling
        print('Message received:', data)
        sender = session.get('username')
        recipient = session.get('name')
        msg = data.get('message')
        if not sender or not recipient:
            logging.error(f"Sender or recipient is not set in the session. Sender: {sender}, Recipient: {recipient}")
            return
        
        if not msg:
            logging.error("Message content is missing.")
            return
        
        
        if "<-mg->" in msg:
            msg=msg.replace("<-mg->", "")
            
        users = User.query.filter(User.username.in_([sender, recipient])).all()
        lg1, lg2 = None, None
        for user in users:
            if user.username == sender:
                lg1 = user.lang
            elif user.username == recipient:
                lg2 = user.lang

        if lg1 and lg2:
            if lg1 == lg2:
                trans_msg = trans_msg2 = msg
            else:
                trans_msg = GoogleTranslator(source=lg1, target=lg2).translate(msg)
                trans_msg2 = GoogleTranslator(source=lg2, target=lg1).translate(msg)

            new_message = Message(content=msg, sender=sender, recipient=recipient)
            db.session.add(new_message)
            db.session.commit()

            timestamp = new_message.timestamp.strftime('%H:%M')
            date = new_message.timestamp.strftime('%d %B')

            message_data = {
                'message': trans_msg,
                'sender': sender,
                'timestamp': timestamp,
                'date': date
            }
            message_data2 = {
                'message': trans_msg2,
                'sender': sender,
                'timestamp': timestamp,
                'date': date
            }

            # send(message_data2, room=sender)
            # send(message_data, room=recipient)
            emit('message', message_data2, room=sender)
            emit('message', message_data, room=recipient)

            print(f"Message from {sender} to {recipient}: {msg} at {timestamp} on {date}")
    except Exception as e:
            logging.error(f"Error handling message: {e}")


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
            print(f"Image sent from {username} to {recipient} at {timestamp} on {date}")
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
            print(f"PDF sent from {username} to {recipient} at {timestamp} on {date}")
        except Exception as e:
            print(f"Error saving PDF: {e}")

logging.basicConfig(filename='email_errors.log', level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def verify(email, html, code):
    try:
        em = MIMEMultipart('alternative')
        em['From'] = 'ayougilzakaria@gmail.com'
        email_pass = 'zwgp yrpp hnvl fugp'
        em['To'] = email
        session['email'] = em['To']

        # Generate the token and prepare email content
        token = generate_token(em['To'])
        em['Subject'] = 'Verify your account'
        html_content = render_template(html, token=token, user=session.get('username'), password=code)
        
        # Attach the HTML content as a MIMEText object
        html_part = MIMEText(html_content, 'html')
        em.attach(html_part)

        # Send the email
        try:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL('smtp.gmail.com', context=context) as smtp:
                smtp.login(em['From'], email_pass)
                smtp.sendmail(em['From'], em['To'], em.as_string())
        except Exception as e:
            logging.error("Error sending email: %s", e)
            return "Error: Unable to send email."

    except Exception as e:
        logging.error("Unexpected error in verify function: %s", e)
        return "Error: An unexpected error occurred."

def generate_token(email):
    try:
        token = secrets.token_urlsafe()
        combined = f"{email}:{token}"
        encoded = base64.urlsafe_b64encode(combined.encode()).decode()
        return encoded
    except Exception as e:
        logging.error("Error generating token: %s", e)
        return None

def decode_token(token):
    try:
        decoded = base64.urlsafe_b64decode(token.encode()).decode()
        email, token_value = decoded.split(':')
        return email
    except Exception as e:
        logging.error("Error decoding token: %s", e)
        return None
users_online = {}

@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    users_online[username] = True
    emit('user_status', {'username': username, 'status': 'online'}, room=room)

@socketio.on('disconnect')
def on_disconnect():
    username = session.get('username')
    if username in users_online:
        del users_online[username]
        emit('user_status', {'username': username, 'status': 'offline'}, broadcast=True)


if __name__ == '__main__':
    app.secret_key = 'my key'
    socketio.run(app, host="0.0.0.0", debug=True)
