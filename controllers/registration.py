from flask import Flask , render_template , request ,redirect, url_for,flash
from werkzeug.security import generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from controllers.model import db,User,Admin


def valid_password(password):
    if len(password) >= 8 and any(char in '!@#$%^&*()_+-=[]{}|;:,.<>?/~' for char in password):
        return True
    return False

def registration():
    if request.method == 'GET':
        return render_template('common/registration.html')
    
    if request.method == 'POST':
        # change after adding admin
        job = request.form.get('job')

        if job == 'user' :
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')
            re_password = request.form.get('re_password')
            qualification = request.form.get('qualification')
            dob = datetime.fromisoformat(request.form.get('dob')).date()

            if not name or not email or not password or not re_password or not dob:
                flash('All fields except qualification are mandatory.')
                return redirect(url_for('registration'))

            user = User.query.filter_by(email=email).first()
            if user :
                flash("Email-Address is already registered.Please proceed to login.")
                return redirect(url_for('login'))
            
            elif password != re_password :
                flash("Password and Confirm Password Should be the Same")
                return render_template('common/registration.html')
            
            elif not valid_password(password):
                flash("Password must be 8 characters long and contain a special character")
                return render_template('common/registration.html')

            else:
                hash_password = generate_password_hash(password)
                new_user = User(name=name,email=email,password=hash_password,qualification=qualification,dob=dob)

                try:
                    db.session.add(new_user)
                    db.session.commit()
                    flash("You Have Registered Successfully. Now You Can Proceed With Login")
                    return redirect(url_for('login'))
                
                except Exception as e:
                    db.session.rollback()
                    flash(f"An error occurred during registration. {str(e)}") 
                    return redirect(url_for('register'))

        # if job == 'admin' :
        #     name = request.form.get('name')
        #     email = request.form.get('email')
        #     password = request.form.get('password')
        #     re_password = request.form.get('re_password')    

        #     if not email or not password or not re_password :
        #         flash('All fields except qualification are mandatory.')
        #         return redirect(url_for('registration'))  

        #     elif password != re_password :
        #         flash("Password and Confirm Password Should be the Same")
        #         return render_template('common/registration.html') 

        #     else:
        #         hash_password = generate_password_hash(password)
        #         admin = Admin(name=name,email=email,password=hash_password)

        #         try:
        #             db.session.add(admin)
        #             db.session.commit()
        #             flash("You Have Registered Successfully. Now You Can Proceed With Login")
        #             return redirect(url_for('login'))
                
        #         except Exception as e:
        #             db.session.rollback()
        #             flash("An error occurred during registration.")
        #             return redirect(url_for('register'))
 



