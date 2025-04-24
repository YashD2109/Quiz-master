from flask import Flask , render_template , request ,redirect, url_for,flash
from flask_login import LoginManager,login_user,login_required,logout_user,current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash


from controllers.model import db,User,Admin,UserLogin
def Login():
    if request.method == 'GET':
        return render_template('common/login.html')
    if request.method == 'POST':
        role = request.form.get('role')
        email = request.form.get('email')
        password = request.form.get('password')

        if role == 'admin':
            admin = Admin.query.filter_by(email=email).first()
            if admin :
                if check_password_hash(admin.password,password):
                    login_user(UserLogin(f"admin_{admin.id}",role,email))
                    return redirect(url_for('admin_dashboard'))
                else :
                    flash("Wrong password.Please try again.")
                    return redirect(url_for('login'))
            else:
                flash("Incorrect email or role chosen!!! please check again.")
                return redirect(url_for('login'))  

        elif role == 'user':
            user = User.query.filter_by(email=email).first()
            if user :
                if check_password_hash(user.password,password):
                    login_user(UserLogin(f"user_{user.id}",role,email))
                    return redirect(url_for('user_dashboard'))
                else :
                    flash("Wrong password.Please try again.")
                    return redirect(url_for('login'))
            else:
                flash("Incorrect email or role chosen!!! please check again.")
                return redirect(url_for('login'))

        else :
            flash("Select user assigned role.")
            return redirect(url_for('login'))


def Logout():
    if request.method == 'GET':
        return render_template('common/logout.html')
    if request.method == 'POST':
        if request.form['logout'] == 'true' :
            logout_user()
            return redirect(url_for('home'))
        else :
            if  current_user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif current_user.role == 'user' :
                return redirect(url_for('user_dashboard'))
    

