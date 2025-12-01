import os
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
from datetime import datetime

from models import db, User, Job, Application
from forms import RegisterForm, LoginForm, JobForm, ApplyForm
from config import Config

# ------------------- Initialize App -------------------
app = Flask(__name__)
app.config.from_object(Config)
app.config['TEMPLATES_AUTO_RELOAD'] = True
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
mail = Mail(app)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ------------------- User Loader -------------------
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# ------------------- Routes -------------------
@app.route('/')
def index():
    jobs = Job.query.all()
    return render_template('index.html', jobs=jobs)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_pw = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful! Please login.", "success")
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash("Login successful!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials", "danger")
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_admin:
        jobs = Job.query.order_by(Job.posted_on.desc()).all()
        applications = Application.query.order_by(Application.applied_on.desc()).all()
        return render_template('admin_dashboard.html', jobs=jobs, applications=applications)
    else:
        jobs = Job.query.order_by(Job.posted_on.desc()).all()
        user_apps = Application.query.filter_by(user_id=current_user.id).all()
        return render_template('dashboard.html', jobs=jobs, applications=user_apps)


@app.route('/admin/applications')
@login_required
def admin_applications():
    if not current_user.is_admin:
        flash("Access denied! Admins only.", "danger")
        return redirect(url_for('dashboard'))

    applications = Application.query.join(User).join(Job).add_columns(
        Application.id,
        User.username.label('applicant_name'),
        User.email.label('applicant_email'),
        Job.title.label('job_title'),
        Application.resume,
        Application.applied_on,
        Application.reviewed
    ).all()

    return render_template('admin_applications.html', applications=applications)


@app.route('/admin/application/<int:app_id>/review', methods=['POST'])
@login_required
def review_application(app_id):
    if not current_user.is_admin:
        flash("Access denied! Admins only.", "danger")
        return redirect(url_for('dashboard'))

    app_record = Application.query.get_or_404(app_id)
    app_record.reviewed = True
    db.session.commit()
    flash(f"Application #{app_id} marked as reviewed.", "success")
    return redirect(url_for('admin_applications'))

@app.route('/admin/job/<int:job_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_job(job_id):
    if not current_user.is_admin:
        flash("Access denied! Admins only.", "danger")
        return redirect(url_for('dashboard'))

    job = Job.query.get_or_404(job_id)
    form = JobForm(obj=job)  # Pre-fill form with existing data

    if form.validate_on_submit():
        job.title = form.title.data
        job.company = form.company.data
        job.location = form.location.data
        job.description = form.description.data
        db.session.commit()
        flash(f"Job '{job.title}' updated successfully!", "success")
        return redirect(url_for('dashboard'))

    return render_template('edit_job.html', form=form, job=job)

@app.route('/admin/job/<int:job_id>/delete', methods=['POST'])
@login_required
def delete_job(job_id):
    if not current_user.is_admin:
        flash("Access denied! Admins only.", "danger")
        return redirect(url_for('dashboard'))

    job = Job.query.get_or_404(job_id)

    # Delete all applications linked to this job
    Application.query.filter_by(job_id=job.id).delete(synchronize_session=False)

    # Then delete the job
    db.session.delete(job)
    db.session.commit()

    flash(f"Job '{job.title}' and all its applications deleted successfully!", "success")
    return redirect(url_for('dashboard'))



@app.route('/post_job', methods=['GET', 'POST'])
@login_required
def post_job():
    if not current_user.is_admin:
        flash("Only admins can post jobs!", "danger")
        return redirect(url_for('dashboard'))
    form = JobForm()
    if form.validate_on_submit():
        job = Job(
            title=form.title.data,
            company=form.company.data,
            location=form.location.data,
            description=form.description.data
        )
        db.session.add(job)
        db.session.commit()
        flash("Job posted successfully!", "success")
        return redirect(url_for('dashboard'))
    return render_template('post_job.html', form=form)



@app.route('/job/<int:job_id>', methods=['GET', 'POST'])
@login_required
def job_detail(job_id):
    job = Job.query.get_or_404(job_id)
    form = ApplyForm()
    if form.validate_on_submit():
        file = form.resume.data
        filename = secure_filename(file.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(path)

        application = Application(user_id=current_user.id, job_id=job.id, resume=filename)
        db.session.add(application)
        db.session.commit()

        try:
            msg = Message(
                subject="Job Application Received",
                sender=app.config['MAIL_USERNAME'],
                recipients=[current_user.email]
            )
            msg.body = f"Hi {current_user.username},\n\nYour application for '{job.title}' has been successfully received."
            mail.send(msg)
        except Exception as e:
            print("Email error:", e)

        flash("Your application has been submitted successfully!", "success")
        return redirect(url_for('dashboard'))
    return render_template('job_detail.html', job=job, form=form)

@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ------------------- Admin Users -------------------
@app.route('/admin/users')
@login_required
def admin_users():
    if not current_user.is_admin:
        flash("Access denied! Admins only.", "danger")
        return redirect(url_for('dashboard'))

    users = User.query.order_by(User.id.desc()).all()
    return render_template('admin_users.html', users=users)


@app.route('/admin/user/<int:user_id>/promote', methods=['POST'])
@login_required
def promote_user(user_id):
    if not current_user.is_admin:
        flash("Access denied!", "danger")
        return redirect(url_for('dashboard'))

    user = User.query.get_or_404(user_id)
    user.is_admin = True
    db.session.commit()
    flash(f"{user.username} is now an admin!", "success")
    return redirect(url_for('admin_users'))


@app.route('/admin/user/<int:user_id>/demote', methods=['POST'])
@login_required
def demote_user(user_id):
    if not current_user.is_admin:
        flash("Access denied!", "danger")
        return redirect(url_for('dashboard'))

    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("You cannot demote yourself!", "warning")
        return redirect(url_for('admin_users'))

    user.is_admin = False
    db.session.commit()
    flash(f"{user.username} is no longer an admin!", "success")
    return redirect(url_for('admin_users'))


@app.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        flash("Access denied!", "danger")
        return redirect(url_for('dashboard'))

    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("You cannot delete yourself!", "warning")
        return redirect(url_for('admin_users'))

    # Optionally delete user's applications
    Application.query.filter_by(user_id=user.id).delete(synchronize_session=False)

    db.session.delete(user)
    db.session.commit()
    flash(f"{user.username} deleted successfully!", "success")
    return redirect(url_for('admin_users'))

@app.route('/search')
@login_required
def search_job():
    query = request.args.get('query', '').strip()
    if not query:
        flash("Please enter a search term.", "warning")
        return redirect(url_for('index'))

    results = Job.query.filter(
        (Job.title.ilike(f"%{query}%")) |
        (Job.company.ilike(f"%{query}%")) |
        (Job.location.ilike(f"%{query}%"))
    ).order_by(Job.posted_on.desc()).all()

    return render_template('search_results.html', jobs=results, query=query)

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        try:
            msg = Message(
                subject=f"Contact Form Submission from {name}",
                sender=app.config['MAIL_USERNAME'],
                recipients=[app.config['MAIL_USERNAME']]  # send to your admin email
            )
            msg.body = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
            mail.send(msg)
            flash("Your message has been sent successfully!", "success")
        except Exception as e:
            print("Email error:", e)
            flash("Failed to send message. Try again later.", "danger")

        return redirect(url_for('contact'))

    return render_template('contact.html')


# ------------------- CLI Commands -------------------
@app.cli.command('init-db')
def init_db():
    db.create_all()
    print("Database initialized successfully.")

@app.cli.command('create-admin')
def create_admin():
    username = input("Enter admin username: ")
    email = input("Enter admin email: ")
    password = input("Enter admin password: ")

    existing = User.query.filter_by(email=email).first()
    if existing:
        print("A user with this email already exists.")
        return

    admin = User(username=username, email=email,
                 password=generate_password_hash(password), is_admin=True)
    db.session.add(admin)
    db.session.commit()
    print("Admin user created successfully!")

# ------------------- Main -------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
