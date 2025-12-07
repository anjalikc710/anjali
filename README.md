Job Portal – Flask Web Application

A fully functional Job Portal built with Flask, featuring user authentication, job posting, applications, admin management, and resume uploads.
Admins can manage jobs, users, and applications, while regular users can search and apply for jobs.

🚀 Features
👤 User Features

Register & Login

View all available jobs

Search jobs by:

Title

Company

Location

Apply to jobs with resume upload

Receive email confirmation for applications

View their own applied jobs

🛠 Admin Features

Admins have full control:

✔ Job Management

Post new jobs

Edit existing jobs

Delete jobs (also deletes related applications)

✔ Application Management

View all applications

Mark applications as reviewed

View applicant details & resume

✔ User Management

View all registered users

Promote user → admin

Demote admin → user

Delete users (removes their applications)

📁 Project Structure
job_portal/
│
├── app.py
├── models.py
├── forms.py
├── config.py
├── requirements.txt
│
├── /templates
│     ├── base.html
│     ├── index.html
│     ├── login.html
│     ├── register.html
│     ├── dashboard.html
│     ├── admin_dashboard.html
│     ├── admin_users.html
│     ├── admin_applications.html
│     ├── job_detail.html
│     ├── post_job.html
│     ├── edit_job.html
│     ├── search_results.html
│
├── /static
│     ├── style.css
│     ├── scripts.js
│
└── /uploads

⚙️ Installation
1. Clone the repository
git clone https://github.com/anjalikc710/anjali.git
cd anjali

2. Create a virtual environment
python -m venv venv

3. Activate the environment

Windows:

venv\Scripts\activate


Mac/Linux:

source venv/bin/activate

4. Install dependencies
pip install -r requirements.txt

🛢 Database Setup

Initialize the database:

flask init-db


Create admin user:

flask create-admin

▶️ Run the Application
python app.py


The app will run at:

http://127.0.0.1:5000

📬 Email Configuration

The project uses Flask-Mail for sending application confirmation emails.

Set the following in your Config:

MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = 'your-email@gmail.com'
MAIL_PASSWORD = 'your-app-password'


Gmail requires an App Password if 2FA is enabled.

🔍 Search Feature

Users can search jobs by:

Title

Company

Location

Search URL:

/search?query=developer

📦 Creating requirements.txt

Use:

pip freeze > requirements.txt

🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first.


