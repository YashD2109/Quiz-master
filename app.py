from flask import Flask , render_template , request ,redirect, url_for,flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager,login_user,login_required,logout_user,current_user
from werkzeug.security import generate_password_hash, check_password_hash
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime,timezone

from controllers.model import db,User,Admin,Subject,Chapter,Quiz,Questions,Scores,UserLogin
from controllers.login import Login,Logout
from controllers.registration import registration
from controllers.admin import adminDashboard,admin_Subject,admin_Chapter,admin_Quiz,manage_Quiz,manage_Question,index_Quiz,userCheck
from controllers.user import userDashboard,user_Subject,user_Chapter,user_Quiz,quiz_Detail,quiz_Test
from controllers.function import leader_Board

app = Flask(__name__,  instance_relative_config=True)
app.config['SQLALCHEMY_DATABASE_URI' ] = "sqlite:///quiz.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key' 
scheduler = BackgroundScheduler()

db.init_app(app)
app.app_context().push()
db.create_all()

login_manager =LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

def quiz_status_update():
    try:
        with app.app_context():
            print("scheduler started")
            now = datetime.now()
            now_int = int(now.strftime("%Y%m%d%H%M%S"))
            quizzes = Quiz.query.all()

            for quiz in quizzes:
                if quiz.startline and quiz.deadline:
                    quiz_start_int = int(quiz.startline.strftime("%Y%m%d%H%M%S"))
                    quiz_deadline_int = int(quiz.deadline.strftime("%Y%m%d%H%M%S"))

                    if quiz.startline and quiz.deadline:
                        if quiz_start_int < now_int:
                            if quiz_deadline_int < now_int:
                                quiz.status = "completed"
                            elif quiz_deadline_int == now_int and quiz.deadline.time() < now.time():
                                quiz.status = "completed"
                            else:
                                quiz.status = "ongoing"
                        elif quiz_start_int == now_int:
                            if quiz.startline.time() <= now.time():
                                if quiz_deadline_int == now_int and quiz.deadline.time() < now.time():
                                    quiz.status = "completed"
                                else:
                                    quiz.status = "ongoing"
                            else:
                                quiz.status = "scheduled"
                        else:
                            quiz.status = "scheduled"

                if not quiz.approved:
                    quiz.status = "draft"

                db.session.commit()

    except Exception as e:
        print(f"Error occurred during quiz status update: {e}")
        db.session.rollback() 
      


def status_updater(scheduler):
    if not scheduler.running:
        scheduler.add_job(
            func=quiz_status_update,
            trigger=IntervalTrigger(seconds=10) 
        )

def shutdown_scheduler():
    # This function is called to safely shutdown the scheduler
    try:
        if scheduler.running:
            print("Shutting down scheduler...")
            scheduler.shutdown(wait=False) 
    except Exception as e:
        print(f"Error shutting down scheduler: {e}")     

if not scheduler.running:
    status_updater(scheduler)
    scheduler.start()



@login_manager.user_loader
def load_user(user_id):
    role, user_id = user_id.split("_")
    if role == 'admin':
        admin = Admin.query.get(int(user_id))
        if admin:
            return UserLogin(f"admin_{admin.id}", "admin",admin.email)
    elif role == 'user':
        user = User.query.get(int(user_id))
        if user:
            return UserLogin(f"user_{user.id}", "user",user.email)
    return None    


# starting index page
@app.route('/')
def home():
    return render_template('common/home.html')

@app.route('/login',methods=['GET','POST'])
def login():
    return Login()

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    return Logout()

@app.route('/registration', methods =['GET','POST'])
def register():
    return registration()

# admin task
@app.route('/admin/dashboard',methods=['GET'])
@login_required
def admin_dashboard():
    return adminDashboard() 
#edit subject
@app.route('/admin/dashboard/subject',methods=['GET','POST'])
@login_required
def admin_subject():
    return admin_Subject()

@app.route('/admin/dashboard/subject/<int:subject_id>/chapter', methods=['GET', 'POST'])
@login_required
def admin_chapter(subject_id):
    return admin_Chapter(subject_id)

@app.route('/admin/dashboard/subject/<int:subject_id>/chapter/<int:chapter_id>', methods=['GET', 'POST'])
@login_required
def admin_quiz(subject_id, chapter_id):
    return admin_Quiz(subject_id, chapter_id)

@app.route('/admin/dashboard/subject/<int:subject_id>/chapter/<int:chapter_id>/quiz',methods =['GET','POST'])
@login_required
def manage_quiz(subject_id, chapter_id):
    return manage_Quiz(subject_id, chapter_id)

@app.route('/admin/dashboard/subject/<int:subject_id>/chapter/<int:chapter_id>/quiz/<int:quiz_id>',methods =['GET','POST'])
@login_required
def manage_question(subject_id,chapter_id,quiz_id):
    return manage_Question(subject_id,chapter_id,quiz_id)

@app.route('/admin/dashboard/subject/<int:subject_id>/chapter/<int:chapter_id>/quiz/<int:quiz_id>/index_quiz',methods =['GET','POST'])
@login_required
def index_quiz(subject_id,chapter_id,quiz_id):
    return index_Quiz(subject_id,chapter_id,quiz_id)


# user task
@app.route('/dashboard',methods =['GET','POST'])
@login_required
def user_dashboard():
    return userDashboard()

@app.route('/dashboard/subject',methods=['GET','POST'])
@login_required
def user_subject():
    return user_Subject()

@app.route('/dashboard/subject/<int:subject_id>/chapter', methods=['GET', 'POST'])
@login_required
def user_chapter(subject_id):
    return user_Chapter(subject_id)

@app.route('/dashboard/subject/<int:subject_id>/chapter/<int:chapter_id>/quiz', methods=['GET', 'POST'])
@login_required
def user_quiz(subject_id, chapter_id):
    return user_Quiz(subject_id, chapter_id)

@app.route('/dashboard/subject/<int:subject_id>/chapter/<int:chapter_id>/quiz/<int:quiz_id>',methods =['GET','POST'])
@login_required
def quiz_detail(subject_id, chapter_id,quiz_id):
    return quiz_Detail(subject_id, chapter_id,quiz_id)

@app.route('/dashboard/subject/<int:subject_id>/chapter/<int:chapter_id>/quiz/<int:quiz_id>/test',methods =['GET','POST'])
@login_required
def quiz_test(subject_id, chapter_id,quiz_id):
    return quiz_Test(subject_id, chapter_id,quiz_id)


@app.route('/dashboard/scoreboard',methods =['GET','POST'])
@login_required
def leader_board():
    return leader_Board()

@app.route('/admin/dashboard/scoreboard',methods =['GET','POST'])
@login_required
def admin_leaderboard():
    return leader_Board()
@app.route('/admin/dashboard/users',methods =['GET','POST'])
@login_required
def usercheck():
    return userCheck()






# @app.teardown_appcontext
# def teardown(exception):
#     shutdown_scheduler()
if __name__ == '__main__':
    app.run(debug = True)