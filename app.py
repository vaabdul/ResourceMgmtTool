from flask import Flask, render_template, request, redirect, url_for,jsonify, flash
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

class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.String(100), nullable=False, unique=True)
    employee_name = db.Column(db.String(100), nullable=False)
    email_id = db.Column(db.String(100), unique=True, nullable=False)
    hiring_manager_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    demand_role = db.Column(db.String(100), nullable=False)
    career_role = db.Column(db.String(100), nullable=False)
    primary_skills = db.Column(db.String(100), nullable=False)
    detail_skill = db.Column(db.Text, nullable=False)
    trained_skill = db.Column(db.Text, nullable=False)
    Years_of_experience = db.Column(db.Integer, nullable=False)
    employee_location = db.Column(db.String(100), nullable=False)
    service_line = db.Column(db.String(100), nullable=False)
    sub_service_line = db.Column(db.String(100), nullable=False)
    region = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    industry_group = db.Column(db.String(100), nullable=False)
    
class ResourceSecondaryInfo(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('resource.emp_id'), primary_key=True)
    experience_level = db.Column(db.String(20), nullable=False)
    doj = db.Column(db.Date, nullable=False)
    last_release_date = db.Column(db.Date, nullable=False)
    last_release_account = db.Column(db.String(100), nullable=False)
    last_release_industry_group = db.Column(db.String(100), nullable=False)
    bench_start_date = db.Column(db.Date, nullable=False)
    aging = db.Column(db.Integer, nullable=False)
    aging_cluster = db.Column(db.String(20), nullable=False)
    bench_classification = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    sub_category = db.Column(db.String(50), nullable=False)
    talent_category = db.Column(db.String(50), nullable=False)
    talent_type = db.Column(db.String(50), nullable=False)
    relocation = db.Column(db.String(3), nullable=False)
    tm_spoc_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    sl_poc_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    profile_available = db.Column(db.String(3), nullable=False)
    action_owner = db.Column(db.String(50), nullable=False)
    wfo = db.Column(db.String(3), nullable=False)
    assessment_score = db.Column(db.String(10), nullable=False)
    proficiency_status = db.Column(db.String(50), nullable=False)
    experience_level_fresher = db.Column(db.String(20), nullable=False)
    
    
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



@app.route('/add_resource', methods=['GET', 'POST'])
def add_resource():
    if request.method == 'POST':
        emp_id = request.form['emp_id']
        employee_name = request.form['employee_name']
        print(request.form['hiring_manager_id'])
        hiring_manager_id = request.form['hiring_manager_id']
        demand_role = request.form['demand_role']
        career_role = request.form['career_role']
        primary_skills = request.form['primary_skills']
        detail_skill = request.form['detail_skill']
        trained_skill = request.form['trained_skill']
        years_of_experience = request.form['years_of_experience']
        employee_location = request.form['employee_location']
        service_line = request.form['service_line']
        sub_service_line = request.form['sub_service_line']
        region = request.form['region']
        country = request.form['country']
        industry_group = request.form['industry_group']
        new_resource = Resource(
            emp_id=emp_id,
            employee_name=employee_name,
            hiring_manager_id=hiring_manager_id,
            demand_role=demand_role,
            career_role=career_role,
            primary_skills=primary_skills,
            detail_skill=detail_skill,
            trained_skill=trained_skill,
            Years_of_experience=int(years_of_experience),
            employee_location=employee_location,
            service_line=service_line,
            sub_service_line=sub_service_line,
            region=region,
            country=country,
            industry_group=industry_group
        )

        db.session.add(new_resource)
        db.session.commit()

        flash('Resource added successfully', 'success')
        return redirect(url_for('add_resource'))

    managers = Employee.query.filter_by(position='Account Manager').all()
    return render_template('dashboard.html', managers=managers)

@app.route('/add_secondary_info', methods=['GET', 'POST'])
def add_secondary_info():
    if request.method == 'POST':
        print(request.form)
        resource_id = request.form['resource_id']
        experience_level = request.form['experience_level']
        doj = datetime.strptime(request.form['doj'], '%Y-%m-%d')
        last_release_date = datetime.strptime(request.form['last_release_date'], '%Y-%m-%d')
        last_release_account = request.form['last_release_account']
        last_release_industry_group = request.form['last_release_industry_group']
        bench_start_date = datetime.strptime(request.form['bench_start_date'], '%Y-%m-%d')
        aging = (datetime.now() - bench_start_date).days
        aging_cluster = request.form['aging_cluster']
        bench_classification = request.form['bench_classification']
        category = request.form['category']
        sub_category = request.form['sub_category']
        talent_category = request.form['talent_category']
        talent_type = request.form['talent_type']
        relocation = request.form['relocation']
        tm_spoc = request.form['tm_spoc']
        sl_poc = request.form['sl_poc']
        profile_available = request.form['profile_available']
        action_owner = request.form['action_owner']
        wfo = request.form['wfo']
        assessment_score = request.form['assessment_score']
        proficiency_status = request.form['proficiency_status']
        experience_level_fresher = request.form['experience_level_fresher']
        print(resource_id)
        secondary_info = ResourceSecondaryInfo(
            id = resource_id,
            experience_level=experience_level,
            doj=doj,
            last_release_date=last_release_date,
            last_release_account=last_release_account,
            last_release_industry_group=last_release_industry_group,
            bench_start_date=bench_start_date,
            aging=aging,
            aging_cluster=aging_cluster,
            bench_classification=bench_classification,
            category=category,
            sub_category=sub_category,
            talent_category=talent_category,
            talent_type=talent_type,
            relocation=relocation,
            tm_spoc_id=tm_spoc,
            sl_poc_id=sl_poc,
            profile_available=profile_available,
            action_owner=action_owner,
            wfo=wfo,
            assessment_score=assessment_score,
            proficiency_status=proficiency_status,
            experience_level_fresher=experience_level_fresher
        )
        db.session.add(secondary_info)
        db.session.commit()
        return redirect('/resources')
    
    tm_spocs = Employee.query.filter_by(position='TM SPOC').all()
    sl_pocs = Employee.query.filter_by(position='SL POC').all()
    return render_template('add_secondary_info.html', tm_spocs=tm_spocs, sl_pocs=sl_pocs)

def get_employee_name(employee_id):
    employee = Employee.query.get(employee_id)
    if employee:
        return employee.name
    else:
        return "Employee not found"

@app.route('/view_resources')
def view_resources():
    resources = Resource.query.all()
    emp = Employee.query.all()
    return render_template('resource.html', resources=resources, employees=emp, get_employee_name=get_employee_name)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True,port=5010)










