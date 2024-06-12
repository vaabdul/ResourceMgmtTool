from flask import Flask, render_template, request, redirect, url_for,jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from configparser import ConfigParser
from flask_jwt_extended import jwt_required,create_access_token,JWTManager # type: ignore
from configparser import ConfigParser
from flask_mail import Mail,Message


app = Flask(__name__)
app.config['SECRET_KEY'] = 'db6c5f48d778e4d356f7234a002bb0acbb41dee209bec32c6f918b70ff2d20b9'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Facade123$@localhost/projectdb'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'lavakishor86@gmail.com' 
app.config['MAIL_PASSWORD'] = 'jpkt praj tmnp mwkj'  
db = SQLAlchemy(app)
mail = Mail(app)
jwt = JWTManager(app)

class Employee(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100),nullable = False)
    email = db.Column(db.String(100),unique=True,nullable = False)
    position = db.Column(db.String(100),nullable = False)
    password = db.Column(db.String(512),nullable = False)

    def set_password(self,password):
        self.password_hash = generate_password_hash(password)

    def check_password(self,password):
        return check_password_hash(self.password,password)
    
def send_registration_email(email, name):
    msg = Message('Welcome to RMT', sender='lavakishor86@gmail.com', recipients=[email])
    msg.body = f"Hi {name},\n\nYou have successfully registered in the RM Tool. Click the link below to login:\n\nhttp://localhost:5010/login"
    mail.send(msg)



# Register route
@app.route('/register',methods = ['POST','GET'])
def register():
    if request.method=='POST':
        name = request.form['name']
        email = request.form['email']
        position = request.form['position']
        password = request.form['password']

        # generate password hash
        password_hash = generate_password_hash(password)

        new_employee = Employee(name=name, email=email, position=position, password=password_hash)
        db.session.add(new_employee)
        db.session.commit()

        # Send registration email
        send_registration_email(email, name)

        return redirect(url_for('success', name=name, email=email, position=position))

    return render_template('register.html')

# Login route
@app.route('/login',methods = ['POST','GET'])
def login():
    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']
        user = Employee.query.filter_by(email=email).first()

        if user and user.check_password(password):
            # generate access tocken
            access_token = create_access_token(identity = email)
            return jsonify({'token':access_token})
        else:
            return jsonify({'error':'Invalid email or password'}),401
    return render_template('login.html')
        
# Logout route
@app.route('/logout', methods=['POST'])
@jwt_required()

def logout():
    # clear the JWT Tocken
    return jsonify({'message':'Successfully logged out'}),200

# @app.route('/')
# def home():
#     return render_template('login.html')

@app.route('/success')
def success():
    name = request.args.get('name')
    email = request.args.get('email')
    position = request.args.get('position')
    return render_template('success.html',name=name,email=email,position=position)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True,port=5010)










