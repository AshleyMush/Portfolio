from flask import Flask, abort, render_template, redirect, url_for, flash, request, send_from_directory
from flask_bootstrap import Bootstrap5
from datetime import datetime
from flask_ckeditor import CKEditor
from werkzeug.security import generate_password_hash, check_password_hash
from email.mime.text import MIMEText
import smtplib
import os
from forms import ContactForm, LoginForm, AddProjectForm, RegisterForm
from models import db, Projects, User
from wtforms import ValidationError
import requests
import json
from flask_login import login_user, LoginManager, login_required, logout_user, current_user




MY_EMAIL_ADDRESS = os.environ.get("EMAIL_KEY")
MY_EMAIL_APP_PASSWORD = os.environ.get("PASSWORD_KEY")

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_APP_KEY")
ckeditor = CKEditor(app)
Bootstrap5(app)

# -----------------Configure DB-------------------------
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///Portfolio.db"
db.init_app(app)

with app.app_context():
    db.create_all()

#----------------------Configure login
login_manager = LoginManager()
login_manager.init_app(app)

# Create a user_loader callback
@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)



#TODO: Remove register form ain snippet and html once registered

@app.route('/', methods=['GET', 'POST'])
def home():
    """
    This function handles the home route of the application. It initializes forms for contact, login, registration,
    and adding a project. It also retrieves the current year and a list of all projects from the database.

    If the contact form is submitted and validated, it sends an email to the user and the admin email.

    If the register form is submitted and validated, it checks if the user already exists. If not, it creates a new
    user instance and adds it to the database.

    If the login form is submitted and validated, it checks the user's credentials. If they are correct, it logs in
    the user and redirects them to the admin home page.

    Finally, it renders the home page with the necessary context variables.

    :return: Rendered template for the home page.
    """
    contact_form = ContactForm()
    login_form = LoginForm()
    register_form = RegisterForm()
    add_project_form = AddProjectForm()

    current_year = datetime.now().year
    list_of_projects = Projects.query.all()
    got_project = False

    if contact_form.validate_on_submit() and contact_form.data:
        """
        if the form is validated, send an email to the user and another to the admin
        """
        name, email, subject, message = contact_form.name.data,\
            contact_form.email.data, contact_form.subject.data, contact_form.message.data

        print(f"{name, email, subject, message}")

        send_confirmation_email(name=name, email=email, subject=subject)
        send_email(name=name, subject=subject, email=email, message=message)

        flash(message='Message Sent Successfully', category='success')


        return render_template('index.html', projects=list_of_projects,
                               current_year=current_year, msg_sent=True,
                               contact_form=contact_form, login_form=login_form, register_form=register_form,
                               add_project_form=add_project_form, got_project = False ,selected_project_id= None,project = None)

    # TODO: remove once registered and deployed
    # ----Register form---#
    if register_form.validate_on_submit() and register_form.data:
        """
        if the form is validated, create a new user instance and add it to the database
        """
        if User.query.first():
            flash("Registration is closed as an admin is already registered.", 'danger')
        else:
            hashed_and_salted_password = generate_password_hash(register_form.password.data,
                                                                method='pbkdf2:sha256',
                                                                salt_length=8)

            new_user = User(
                name=register_form.name.data,
                email=register_form.email.data,
                password=hashed_and_salted_password
            )
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('home'))

    if login_form.validate_on_submit() and login_form.data:
        """
        if the form is validated, login the user
        """
        login_email = login_form.email.data
        login_password = login_form.password.data

        user = User.query.filter_by(email=login_email).first()

        if user and check_password_hash(user.password, login_password):
            login_user(user)
            flash('Logged in successfully', 'success')
            return redirect(url_for('admin_home'))

        flash('Login Failed. Check your email and password.', 'danger')

    return render_template('index.html', projects=list_of_projects, current_year=current_year, msg_sent=False,
                           contact_form=contact_form, login_form=login_form, register_form=register_form, add_project_form=add_project_form,got_project = False, selected_project_id= None, project = None)







#----------------------------------------------------------------------Add project
# Todo: Create instance of db and  pasrse  projects to projects.html
@app.route('/projects', methods=['GET', 'POST'])
def all_projects():
    list_of_projects = Projects.query.all()
    return render_template('all-projects.html', projects=list_of_projects)



#-------------------------Admin home
@app.route('/admin-home', methods=['GET', 'POST'])
@login_required
def admin_home():
    """
    Add Docstrings here to explain what this function does
    :return:
    """

    print("Admin Dashboard")
    login_form = LoginForm()
    register_form = RegisterForm()
    contact_form = ContactForm()
    add_project_form = AddProjectForm()
    current_year = datetime.now().year
    list_of_projects = Projects.query.all()
    logged_in = True

    if contact_form.validate_on_submit() and contact_form.data:
        """
        if the form is validated and has data on the fields required, send an email to the user and another to the admin
        """
        name, email, subject, message = contact_form.name.data,\
            contact_form.email.data, contact_form.subject.data, contact_form.message.data

        print(f"{name, email, subject, message}")

        send_confirmation_email(name=name, email=email, subject=subject)
        send_email(name=name, subject=subject, email=email, message=message)

        return render_template('index.html', projects=list_of_projects,
                               current_year=current_year, msg_sent=True,
                                 contact_form=contact_form, login_form=login_form,request_form=register_form,

                               add_project_form=add_project_form, )




    if add_project_form.validate_on_submit() and add_project_form.data:
        """
        if the form is validated and has data on the fields required, create a new project instance and add it to the database
        """
        new_project = Projects(
            name=add_project_form.name.data,
            homepage_thumbnail=add_project_form.homepage_thumbnail.data,
            img_url=add_project_form.img_url.data,
            video_url=add_project_form.video_url.data,
            category=add_project_form.category.data,
            tech_used=add_project_form.tech_used.data,
            project_url=add_project_form.project_url.data,
            description=add_project_form.description.data
        )
        print(new_project)
        db.session.add(new_project)
        db.session.commit()
        flash('Project added successfully', 'success')

        return redirect(url_for('admin_home'))
    else:
        flash('Project not added. Please check the form and try again.', 'danger')

    return render_template('index.html', projects=list_of_projects, current_year=current_year, msg_sent=False,
                            contact_form=contact_form, login_form=login_form, register_form= register_form, add_project_form=add_project_form)





#HTTP -Get a specific item
@app.route('/project/<int:id>', methods=['GET'])
def get_project(id):
    print(f'Now in GET-PROJECT {id}')
    contact_form = ContactForm()
    login_form = LoginForm()
    register_form = RegisterForm()
    add_project_form = AddProjectForm()

    current_year = datetime.now().year
    selected_project = Projects.query.get_or_404(id)
    list_of_projects = Projects.query.all()
    got_project = True


    print(f"Selected project: {selected_project.name}")

    #----Contact form logic---#
    if contact_form.validate_on_submit() and contact_form.data:
        """
        if the form is validated, send an email to the user and another to the admin
        """
        name, email, subject, message = contact_form.name.data,\
            contact_form.email.data, contact_form.subject.data, contact_form.message.data

        print(f"{name, email, subject, message}")

        send_confirmation_email(name=name, email=email, subject=subject)
        send_email(name=name, subject=subject, email=email, message=message)

        flash(message='Message Sent Successfully', category='success')


        return render_template('index.html', projects=list_of_projects,
                               current_year=current_year, msg_sent=True,
                               contact_form=contact_form, login_form=login_form, register_form=register_form,
                               add_project_form=add_project_form,  project=selected_project, selected_project_id= selected_project.id,got_project = True)

    # TODO: remove once registered and deployed
    # ----Register form logic---#
    if register_form.validate_on_submit() and register_form.data:
        """
        if the form is validated, create a new user instance and add it to the database
        """
        if User.query.first():
            flash("Registration is closed as an admin is already registered.", 'danger')
        else:
            hashed_and_salted_password = generate_password_hash(register_form.password.data,
                                                                method='pbkdf2:sha256',
                                                                salt_length=8)

            new_user = User(
                name=register_form.name.data,
                email=register_form.email.data,
                password=hashed_and_salted_password
            )
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! You can now log in.', 'success')

            return redirect(url_for('get_project'))


    # ----Login form logic---#
    if login_form.validate_on_submit() and login_form.data:
        """
        if the form is validated, login the user
        """
        login_email = login_form.email.data
        login_password = login_form.password.data

        user = User.query.filter_by(email=login_email).first()

        if user and check_password_hash(user.password, login_password):
            login_user(user)
            flash('Logged in successfully', 'success')
            return redirect(url_for('home'))

        flash('Login Failed. Check your email and password.', 'danger')

    print(f'Sending {selected_project.name} to index.html')

    return render_template('project.html', projects=list_of_projects, current_year=current_year, msg_sent=False,
                           contact_form=contact_form, login_form=login_form, register_form=register_form, add_project_form=add_project_form, project=selected_project, selected_project_id= selected_project.id,got_project = True)




@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'Success')
    return  redirect(url_for('home'))




@app.route('/delete-project/<int:id>', methods=['DELETE'])
def delete_project(id):
    project = Projects.query.get_or_404(id)
    db.session.delete(project)
    db.session.commit()

    return redirect(url_for('admin-home'))



@app.route('/delete-user/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()

    return "deleted"






























# API - Get all items



# HTTP- Create item
#Todo: create new project instance
#Todo: Change the instance variables to a dict
# Todo: use requests to post it
# Todo: Redirect to url_for( 'All_projects



# API HTTP - Create item
"""@app.route('/add', methods=[ 'POST'])
def add_project():
    if request.method == 'POST':
        new_project = {
            'name': request.form.get('name'),
            'homepage_thumbnail': request.form.get('homepage_thumbnail'),
            'img_url': request.form.get('img_url'),
            'video_url': request.form.get('video_url'),
            'category': request.form.get('category'),
            'tech_used': request.form.get('tech_used'),
            'project_url': request.form.get('project_url'),
            'description': request.form.get('description')
        }
        response = requests.post(url=f"{BASE_URL}/insert-to-db", data=new_project)
        if response.status_code == 201:
            return redirect(url_for('all_projects'))
        else:
            return f"Error: Could not add project {new_project['name']}"
    return render_template('add_project.html')"""


# TODO Make this app an app and front end app because I have to make the api seperately with the db and then the app

# HTTP -  API Update item

"""@app.route('/patch/<int:id>', methods=['Patch'])
def send_patch_to_api(id):
    selected_project = db.get_or_404(Projects, id)
    if request.method =="PATCH":
        if request.method == 'PATCH':
            update_data = {
                'name': request.form.get('name'),
                'homepage_thumbnail': request.form.get('homepage_thumbnail'),
                'img_url': request.form.get('img_url'),
                'video_url': request.form.get('video_url'),
                'category': request.form.get('category'),
                'tech_used': request.form.get('tech_used'),
                'project_url': request.form.get('project_url'),
                'description': request.form.get('description')
            }

            response = requests.patch(url=f"{BASE_URL}/patch/{id}", data=update_data)
            if response.status_code == 200:
                return redirect(url_for('all_projects'))
            else:
                return f"Error: Could not update project {selected_project.name}"""""

"""
@app.route('/put/<int:id>', methods=['PUT'])
def send_put_to_api(id):
    selected_project = db.get_or_404(Projects, id)
    if request.method =="PUT":
        if request.method == 'PUT':
            update_data = {
                'name': request.form.get('name'),
                'homepage_thumbnail': request.form.get('homepage_thumbnail'),
                'img_url': request.form.get('img_url'),
                'video_url': request.form.get('video_url'),
                'category': request.form.get('category'),
                'tech_used': request.form.get('tech_used'),
                'project_url': request.form.get('project_url'),
                'description': request.form.get('description')
            }

            response = requests.put(url=f"{BASE_URL}/put/{id}", data=update_data)
            if response.status_code == 200:
                return redirect(url_for('all_projects'))
            else:
                return f"Error: Could not update project {selected_project.name}
"""""

















#
#
# # HTTP -Get a specific item
# @app.route('/<int:id>', methods=['GET'])
# def get_project(id):
#     login_form = LoginForm()
#     form = ContactForm()
#     current_year = datetime.now().year
#
#     list_of_projects = Projects.query.all()
#
#
# #TODO: Get projects from api
#     response = requests.get(url=f'http://127.0.0.1:5002/api/project/{id}')
#     data   = response.json()
#     project = data
#
#
#
#     if form.validate_on_submit() and form.data:
#         name, email, subject, message = form.name.data, form.email.data, form.subject.data, form.message.data
#
#         print(f"{name, email, subject, message}")
#
#         send_confirmation_email(name=name, email=email, subject=subject)
#         send_email(name=name, subject=subject, email=email, message=message)
#
#         return render_template('project.html',project = project, current_year=current_year, msg_sent=True, form=form
#                             , projects=list_of_projects, login_form=login_form)
#
#     return render_template('project.html', project = project,current_year=current_year, msg_sent=False, form=form,
#                            projects=list_of_projects, login_form=login_form)


@app.route('/download', methods=['GET', 'POST'])
def download():
    return send_from_directory('static', path="files/CV.pdf", as_attachment=True)


def send_confirmation_email(name, email, subject, service='gmail'):
    # Email content
    email_content = render_template('thanks.html', name=name)

    # MIMEText logic
    msg = MIMEText(email_content, 'html')
    msg['From'] = MY_EMAIL_ADDRESS
    msg['To'] = email  # Send to the user's email
    msg['Subject'] = f"Confirmation: {subject}"
    msg['Reply-To'] = MY_EMAIL_ADDRESS

    # ---SMTP logic-----

    smtp_settings = {
        'gmail': ('smtp.gmail.com', 587),
        'yahoo': ('smtp.mail.yahoo.com', 587),
        'outlook': ('smtp.office365.com', 587)
        # Add more services as needed
    }

    if service in smtp_settings:
        smtp_server, smtp_port = smtp_settings[service]
    else:
        raise ValueError("Unsupported email service")

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as connection:
            connection.starttls()
            connection.login(MY_EMAIL_ADDRESS, MY_EMAIL_APP_PASSWORD)
            connection.sendmail(MY_EMAIL_ADDRESS, email, msg.as_string())
    except Exception as e:
        print(f"Error sending email: {e}")
        render_template('index.html')


def send_email(name, subject, email, message, service='gmail'):
    email_content = render_template('email-template.html', name=name, subject=subject, email=email,
                                    message=message)

    # -- MIMETEXT logic ---

    msg = MIMEText(email_content, 'html')
    msg['From'] = email
    msg['To'] = MY_EMAIL_ADDRESS
    msg['Subject'] = f"New message from {name}: {subject}"
    msg['Reply-To'] = email

    # ---SMTP logic-----

    smtp_settings = {
        'gmail': ('smtp.gmail.com', 587),
        'yahoo': ('smtp.mail.yahoo.com', 587),
        'outlook': ('smtp.office365.com', 587)
        # Add more services as needed
    }

    if service in smtp_settings:
        smtp_server, smtp_port = smtp_settings[service]
    else:
        raise ValueError("Unsupported email service")

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as connection:
            connection.starttls()
            connection.login(MY_EMAIL_ADDRESS, MY_EMAIL_APP_PASSWORD)
            connection.sendmail(from_addr=email, to_addrs=MY_EMAIL_ADDRESS,
                                msg=msg.as_string())
    except Exception as e:
        print(f"Error sending email: {e}")
        render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True, port=5002)
