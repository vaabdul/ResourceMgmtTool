from flask import Flask, render_template, request, redirect, url_for,jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from configparser import ConfigParser
from flask_jwt_extended import jwt_required,create_access_token,JWTManager # type: ignore
from configparser import ConfigParser
from flask_mail import Mail,Message
from flask import Flask, request, redirect, url_for, send_from_directory, flash
from werkzeug.utils import secure_filename
from flask_migrate import Migrate
from sqlalchemy import cast
from sqlalchemy.types import String
import os
from datetime import datetime
from flask import request


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
    emp_id = db.Column(db.Integer, nullable=False, unique=True)
    employee_name = db.Column(db.String(100), nullable=False)
    email_id = db.Column(db.String(100), unique=True, nullable=False)
    hiring_manager_id = db.Column(db.Integer, db.ForeignKey('employee.id', ondelete='SET NULL'), nullable=True)
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
    hiring_manager = db.relationship('Employee', foreign_keys=[hiring_manager_id], passive_deletes=True)
    secondary_info = db.relationship('ResourceSecondaryInfo', backref='resource', uselist=False)
    
    
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
    tm_spoc_id = db.Column(db.Integer, db.ForeignKey('employee.id', ondelete='SET NULL'), nullable=True)
    sl_poc_id = db.Column(db.Integer, db.ForeignKey('employee.id', ondelete='SET NULL'), nullable=True)
    profile_available = db.Column(db.String(3), nullable=False)
    action_owner = db.Column(db.String(50), nullable=False)
    wfo = db.Column(db.String(3), nullable=False)
    assessment_score = db.Column(db.String(10), nullable=False)
    proficiency_status = db.Column(db.String(50), nullable=False)
    experience_level_fresher = db.Column(db.String(20), nullable=False)
    resume_path = db.Column(db.String(200), nullable=True)  # New field for resume file path

    tm_spoc = db.relationship('Employee', foreign_keys=[tm_spoc_id], passive_deletes=True)
    sl_poc = db.relationship('Employee', foreign_keys=[sl_poc_id], passive_deletes=True)
    
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
        return render_template('login.html',name=name, email=email, position=position)
        # return redirect(url_for('success', name=name, email=email, position=position))

    return render_template('register.html')

# Login route
@app.route('/login',methods = ['GET','POST'])
def login():
    if request.method=='POST':
        email = request.form['email']
        password = request.form['password']
        user = Employee.query.filter_by(email=email).first()
        if user and user.check_password(password):
            if user.position == 'Account Manager':
                return redirect(url_for('resources_by_manager', manager_id=user.id))
            elif user.position == 'Admin':
                access_token = create_access_token(identity = email)
                managers = Employee.query.filter_by(position='Account Manager').all()
                return redirect(url_for('view_resources'))
            else:
                return render_template('login.html', message = "No authentication for login please contact Admin")
            # # generate access tocken
            # access_token = create_access_token(identity = email)
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
        Email = request.form['email_id']
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
            email_id = Email,
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
        tm_spocs = Employee.query.filter_by(position='TM SPOC').all()
        sl_pocs = Employee.query.filter_by(position='SL POC').all()
        return render_template('add_secondary_info.html', tm_spocs=tm_spocs, sl_pocs=sl_pocs,resource_id = emp_id )
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
        aging_cluster = '1-30' if 0 < aging <= 30 else '30-60' if 30 < aging <= 60 else '60-90' if 60 < aging <= 90 else 'above 90'
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
        if 'resume' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['resume']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
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
            experience_level_fresher=experience_level_fresher,
            resume_path = filename
        )
        db.session.add(secondary_info)
        db.session.commit()
        return redirect('add_resource')
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

@app.route('/resource/<emp_id>', methods=['GET'])
def view_resource(emp_id):
    resource = Resource.query.filter_by(emp_id=emp_id).first()
    secondary_info = ResourceSecondaryInfo.query.filter_by(id=emp_id).first()
    return render_template('singleemp.html', resource=resource,  get_employee_name=get_employee_name, data = secondary_info)
    
@app.route('/update_resource/<int:id>', methods=['GET', 'POST'])
# @jwt_required
def update_resource(id):
    resource = Resource.query.get_or_404(id)
    if request.method == 'POST':
        resource.employee_name = request.form['employee_name']
        resource.email_id = request.form['email_id']
        resource.hiring_manager_id = request.form['hiring_manager_id']
        resource.demand_role = request.form['demand_role']
        resource.career_role = request.form['career_role']
        resource.primary_skills = request.form['primary_skills']
        resource.detail_skill = request.form['detail_skill']
        resource.trained_skill = request.form['trained_skill']
        resource.Years_of_experience = int(request.form['years_of_experience'])
        resource.employee_location = request.form['employee_location']
        resource.service_line = request.form['service_line']
        resource.sub_service_line = request.form['sub_service_line']
        resource.region = request.form['region']
        resource.country = request.form['country']
        resource.industry_group = request.form['industry_group']
        db.session.commit()
        flash('Resource updated successfully', 'success')
        tm_spocs = Employee.query.filter_by(position='TM SPOC').all()
        sl_pocs = Employee.query.filter_by(position='SL POC').all()
        emp_id = int(resource.emp_id)
        print(emp_id)
        return render_template('update_secondary_info.html', secondary_info=ResourceSecondaryInfo.query.filter_by(id=emp_id).first(), tm_spocs=tm_spocs, sl_pocs=sl_pocs)
    managers = Employee.query.filter_by(position='Account Manager').all()
    return render_template('update_resource.html', resource=resource, managers=managers)

@app.route('/update_secondary_info/<int:id>', methods=['GET', 'POST'])
def update_secondary_info(id):
    secondary_info = ResourceSecondaryInfo.query.get_or_404(id)
    if request.method == 'POST':
        secondary_info.experience_level = request.form['experience_level']
        secondary_info.doj = datetime.strptime(request.form['doj'], '%Y-%m-%d')
        secondary_info.last_release_date = datetime.strptime(request.form['last_release_date'], '%Y-%m-%d')
        secondary_info.last_release_account = request.form['last_release_account']
        secondary_info.last_release_industry_group = request.form['last_release_industry_group']
        secondary_info.bench_start_date = datetime.strptime(request.form['bench_start_date'], '%Y-%m-%d')
        secondary_info.aging = (datetime.now() - secondary_info.bench_start_date).days
        secondary_info.aging_cluster = request.form['aging_cluster']
        secondary_info.bench_classification = request.form['bench_classification']
        secondary_info.category = request.form['category']
        secondary_info.sub_category = request.form['sub_category']
        secondary_info.talent_category = request.form['talent_category']
        secondary_info.talent_type = request.form['talent_type']
        secondary_info.relocation = request.form['relocation']
        secondary_info.tm_spoc_id = request.form['tm_spoc']
        secondary_info.sl_poc_id = request.form['sl_poc']
        secondary_info.profile_available = request.form['profile_available']
        secondary_info.action_owner = request.form['action_owner']
        secondary_info.wfo = request.form['wfo']
        secondary_info.assessment_score = request.form['assessment_score']
        secondary_info.proficiency_status = request.form['proficiency_status']
        secondary_info.experience_level_fresher = request.form['experience_level_fresher']
        if 'resume' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['resume']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
        secondary_info.resume_path = filename
        db.session.commit()
        flash('Secondary info updated successfully', 'success')
        return redirect(url_for('view_resources'))
    tm_spocs = Employee.query.filter_by(position='TM SPOC').all()
    sl_pocs = Employee.query.filter_by(position='SL POC').all()
    return render_template('update_secondary_info.html', secondary_info=secondary_info, tm_spocs=tm_spocs, sl_pocs=sl_pocs)


@app.route('/delete_resource/<int:id>', methods=['POST'])
# @jwt_required()
def delete_resource(id):
    resource = Resource.query.get_or_404(id)
    secondary_info = ResourceSecondaryInfo.query.filter_by(id=resource.emp_id).first()
    if secondary_info:
        db.session.delete(secondary_info)
        db.session.commit()
    db.session.delete(resource)
    db.session.commit()
    flash('Resource and related secondary info deleted successfully', 'success')
    return redirect(url_for('view_resources'))

@app.route('/view_resources', methods=["GET", "POST"])
def view_resources():
    resources = []
    secondary_imp = {}
    emp = Employee.query.all()
    
    if request.method == "POST":
        # Handle search query
        search_query = request.form.get('search')
        if search_query:
            # Get employee id for the search query if it exists
            employee_id = get_employee_id(search_query)
            employee_id_str = str(employee_id) if employee_id else ""

            # Primary resource query
            resources = Resource.query.filter(
                (Resource.employee_name.ilike(f"%{search_query}%")) |
                (cast(Resource.emp_id, String).ilike(f"%{search_query}%")) |
                (Resource.email_id.ilike(f"%{search_query}%")) |
                (Resource.demand_role.ilike(f"%{search_query}%")) |
                (cast(Resource.hiring_manager_id, String).ilike(f"%{employee_id_str}%")) |
                (Resource.career_role.ilike(f"%{search_query}%")) |
                (Resource.primary_skills.ilike(f"%{search_query}%")) |
                (Resource.detail_skill.ilike(f"%{search_query}%")) |
                (Resource.trained_skill.ilike(f"%{search_query}%")) |
                (Resource.employee_location.ilike(f"%{search_query}%")) |
                (Resource.service_line.ilike(f"%{search_query}%")) |
                (Resource.sub_service_line.ilike(f"%{search_query}%")) |
                (Resource.region.ilike(f"%{search_query}%")) |
                (Resource.country.ilike(f"%{search_query}%")) |
                (Resource.industry_group.ilike(f"%{search_query}%"))
            ).all()
            
            secondary_imp = {r.emp_id: ResourceSecondaryInfo.query.filter_by(id=r.emp_id).first() for r in resources}
            
            if not resources:
                # Secondary resource query
                secondary_resources = ResourceSecondaryInfo.query.filter(
                    (cast(ResourceSecondaryInfo.experience_level, String).ilike(f"%{search_query}%")) |
                    (cast(ResourceSecondaryInfo.aging, String).ilike(f"%{search_query}%")) |
                    (cast(ResourceSecondaryInfo.doj, String).ilike(f"%{search_query}%")) |
                    (cast(ResourceSecondaryInfo.last_release_date, String).ilike(f"%{search_query}%")) |
                    (cast(ResourceSecondaryInfo.last_release_account, String).ilike(f"%{search_query}%")) |
                    (cast(ResourceSecondaryInfo.last_release_industry_group, String).ilike(f"%{search_query}%")) |
                    (cast(ResourceSecondaryInfo.bench_start_date, String).ilike(f"%{search_query}%")) |
                    (cast(ResourceSecondaryInfo.aging, String).ilike(f"%{search_query}%")) |
                    (cast(ResourceSecondaryInfo.aging_cluster, String).ilike(f"%{search_query}%")) |
                    (cast(ResourceSecondaryInfo.bench_classification, String).ilike(f"%{search_query}%")) |
                    (cast(ResourceSecondaryInfo.category, String).ilike(f"%{search_query}%")) |
                    (cast(ResourceSecondaryInfo.sub_category, String).ilike(f"%{search_query}%")) |
                    (cast(ResourceSecondaryInfo.talent_category, String).ilike(f"%{search_query}%")) |
                    (cast(ResourceSecondaryInfo.talent_type, String).ilike(f"%{search_query}%")) |
                    (cast(ResourceSecondaryInfo.relocation, String).ilike(f"%{search_query}%")) |
                    (cast(ResourceSecondaryInfo.tm_spoc_id, String).ilike(f"%{employee_id_str}%")) |
                    (cast(ResourceSecondaryInfo.sl_poc_id, String).ilike(f"%{employee_id_str}%")) |
                    (cast(ResourceSecondaryInfo.profile_available, String).ilike(f"%{search_query}%")) |
                    (cast(ResourceSecondaryInfo.action_owner, String).ilike(f"%{search_query}%")) |
                    (cast(ResourceSecondaryInfo.wfo, String).ilike(f"%{search_query}%")) |
                    (cast(ResourceSecondaryInfo.assessment_score, String).ilike(f"%{search_query}%")) |
                    (cast(ResourceSecondaryInfo.proficiency_status, String).ilike(f"%{search_query}%")) |
                    (cast(ResourceSecondaryInfo.experience_level_fresher, String).ilike(f"%{search_query}%"))
                ).all()
                
                secondary_imp = {sr.id: sr for sr in secondary_resources}
                resource_ids = [sr.id for sr in secondary_resources]
                resources = Resource.query.filter(Resource.emp_id.in_(resource_ids)).all()
                
    if not resources:
        resources = Resource.query.all()
        secondary_imp = {r.emp_id: ResourceSecondaryInfo.query.filter_by(id=r.emp_id).first() for r in resources}
    
    return render_template('dashboard1.html', resources=resources, employees=emp, get_employee_name=get_employee_name, secondary_imp=secondary_imp)


@app.route('/resources_by_manager/<int:manager_id>', methods=['GET'])
# @jwt_required()
def resources_by_manager(manager_id):
    category = request.args.get('category')
    aging_cluster = request.args.get('aging_cluster')
    employee_name = request.args.get('employee_name')

    # Start building the base query
    query = Resource.query.filter_by(hiring_manager_id=manager_id)

    # Apply filters based on parameters received
    if employee_name:
        query = query.filter(Resource.employee_name.ilike(f"%{employee_name}%"))

    resources = query.all()

    if category:
        secondary_infos = {r.emp_id: ResourceSecondaryInfo.query.filter_by(id=r.emp_id, category=category).first() for r in resources}
        resources = [r for r in resources if secondary_infos[r.emp_id] is not None]
    elif aging_cluster:
        secondary_infos = {r.emp_id: ResourceSecondaryInfo.query.filter_by(id=r.emp_id, aging_cluster=aging_cluster).first() for r in resources}
        resources = [r for r in resources if secondary_infos[r.emp_id] is not None]
    else:
        secondary_infos = {r.emp_id: ResourceSecondaryInfo.query.filter_by(id=r.emp_id).first() for r in resources}

    # Assuming categories and aging clusters are predefined lists or fetched from the database
    categories = ["Available Allocation", "Billing", "New"]  # Replace with actual categories
    aging_clusters = ["1-30", "30-60", "60-90", "90 and above"]

    # Get list of resource names for filtering dropdown
    resource_names =[]
    for i in query:
        # print(i.employee_name)
        resource_names.append(i.employee_name)

    return render_template('category.html',
                           resources=resources,
                           get_employee_name=get_employee_name,
                           secondary_infos=secondary_infos,
                           categories=categories,
                           selected_category=category,
                           aging_clusters=aging_clusters,
                           selected_aging_cluster=aging_cluster,
                           manager_id=manager_id,
                           resource_names=resource_names,
                           selected_employee_name=employee_name)

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload_resume/<int:emp_id>', methods=['POST'])
def upload_resume(emp_id):
    print("okkkkkkk")
    if 'resume' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['resume']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        resource_info = ResourceSecondaryInfo.query.filter_by(id=emp_id).first()
        resource_info.resume_path = file_path
        db.session.commit()

        flash('Resume successfully uploaded')
        return redirect(url_for('view_resource', emp_id=emp_id))

@app.route('/uploads/<filename>')
def download_resume(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True,port=5010)










