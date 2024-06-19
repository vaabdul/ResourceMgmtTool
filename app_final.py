from flask import Flask, jsonify, session, url_for, render_template,request,redirect
from flask_sqlalchemy import SQLAlchemy # type: ignore
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash
from configparser import ConfigParser
from flask_jwt_extended import jwt_required,create_access_token,JWTManager # type: ignore
from configparser import ConfigParser
from flask_mail import Mail,Message # type: ignore
from wtforms import SelectField,FileField  # type: ignore
from flask_wtf.file import FileAllowed, FileRequired # type: ignore



app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:lavakishor14@localhost/ResourceManagementTool_db'
db = SQLAlchemy(app)
mail = Mail(app)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'db6c5f48d778e4d356f7234a002bb0acbb41dee209bec32c6f918b70ff2d20b9'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:lavakishor14@localhost/ResourceManagementTool_db'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'lavakishor86@gmail.com' 
app.config['MAIL_PASSWORD'] = 'jpkt praj tmnp mwkj'  
db = SQLAlchemy(app)
mail = Mail(app)
jwt = JWTManager(app)


class Admin(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100),nullable = False)
    email = db.Column(db.String(100),unique=True,nullable = False)
    category = db.Column(db.SelectField('Category', choices=[('Admin', 'Admin'),('Delivery Manager', 'Delivery Manager')))])
    password = db.Column(db.String(512),nullable = False)

    def set_password(self,password):
        self.password_hash = generate_password_hash(password)

    def check_password(self,password):
        return check_password_hash(self.password,password)
    
def send_registration_email(email, name):
    msg = Message('Welcome to RMT', sender='lavakishor86@gmail.com', recipients=[email])
    msg.body = f"Hi {name},\n\nYou have successfully registered in the RM Tool. Click the link below to login:\n\nhttp://localhost:5000/login"
    mail.send(msg)


class Resource(db.Model):
    empid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100),nullable = False)
    email = db.Column(db.String(100),unique=True,nullable = False)
    phone = db.Column(db.String(100), unique=True, nullable=False)
    resume = FileField('Resume', validators=[FileRequired(),FileAllowed(['pdf', 'doc', 'docx'], 'PDF and Word documents only!')])
    address = db.Column(db.String(200),nullable = False)
    joining_date = db.Column(db.DateTime(timezone=True), server_default=func.now())
    total_projects = db.Column(db.Integer, default=1)
    total_test_case = db.Column(db.Integer, default=1)
    total_defects_found = db.Column(db.Integer, default=1)
    total_defects_pending = db.Column(db.Integer, default=1)





@app.route('/')
def index():
    return render_template('home.html')

@app.route('/login',methods=['POST','GET'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = Admin.query.filter_by(email=email).first()

        if user and user.check_password(password):
            # generate access tocken
            access_tocken = create_access_token(identity=email)
            # store the tocken in session
            session['access_token'] = access_tocken
            # redirect to dashboard

            if user.category == 'Admin':
                return redirect(url_for('dashboard')) 
            elif user.category == "Delivery Manager":
                return redirect(url_for('manager'))   
        else:
            error = "Password did not match"

    return render_template('login.html',loginerror = error)

@app.route('/register',methods=['POST','GET'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        category = request.form['category']

        existing_user = Admin.query.filter((Admin.email == email) | (Admin.name == name)).first()
        
        if existing_user:
            return render_template('register.html',registererror = 'Username or email already taken,try with differenet username or email. ')
        # generate password hash
        password_hash = generate_password_hash(password)

        new_admin = Admin(name=name,email=email,password=password_hash,category=category)
        db.session.add(new_admin)
        db.session.commit()

        # send registraction mail 

        send_registration_email(email,name)
        return redirect(url_for('sucess',name=name,email=email,passord=password,category=category))
    return render_template('register.html')


@app.route('/dashboard',methods = ["POST","GET"])
def dashboard():
    if request.method == "POST":
        pass
    employees = Resource.query.all()
    return render_template('dashboard.html',employees=employees)

@app.route('/addnewemployee',methods = ["POST","GET"])
def addnewemployee():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        new_employee = Resource(name = name, email = email, phone = phone, address = address)
        db.session.add(new_employee)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('addnewemployee.html')



@app.route('/dashboards', methods=["GET", "POST"])
def dashboards():
    if request.method == "POST":
        # Handle search query
        search_query = request.form.get('search')
        if search_query:
            employees = Resource.query.filter(
                (Resource.name.ilike(f"%{search_query}%")) |
                (Resource.email.ilike(f"%{search_query}%")) |
                (Resource.phone.ilike(f"%{search_query}%")) |
                (Resource.address.ilike(f"%{search_query}%"))
            ).all()
        else:
            employees = Resource.query.all()
    else:
        employees = Resource.query.all()
    return render_template('dashboard.html', employees=employees)


@app.route('/singleemployee/<int:empid>')
def singleemployee(empid):
    employee = Resource.query.get(empid)
    if employee is None:
        return "Employee not found",404

    return render_template('singleemployee.html',employee=employee)

@app.route('/fetchone/<int:empid>')
def fetchone(empid):
    employee = Resource.query.get(empid)
    return render_template('updateemployee.html',employee=employee)


@app.route('/updateemployee', methods=["POST", "GET"])
def updateemployee():
    if request.method == "POST":
        empid = request.form['empid']
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        
        employee = Resource.query.get(empid)

        if employee:
            employee.name = name
            employee.email = email
            employee.phone = phone
            employee.address = address

            db.session.commit()

            return redirect(url_for('dashboard'))

    return render_template('updateemployee.html')

@app.route('/deleteemp/<int:empid>', methods=['POST'])
def deleteemp(empid):
    employee = Resource.query.get_or_404(empid)

    if request.method == 'POST':
        db.session.delete(employee)
        db.session.commit()
        return redirect(url_for('dashboard'))

    return render_template('dashboard.html')


@app.route('/logout')
def logout():
    # Clear the session data
    session.clear()
    
    return render_template('home.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print('done')
    app.run(debug=True)


