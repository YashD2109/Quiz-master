from flask import Flask , render_template , request ,redirect, url_for,flash,jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime ,timezone
from flask_login import LoginManager,login_user,login_required,logout_user,current_user
from controllers.model import db,User,Admin,Subject,Chapter,Quiz,Questions,Scores,UserLogin
from controllers.login import Login,Logout
from controllers.registration import registration
from controllers.function import get_total_score,get_total_marks,quiz_approve,user_allow

def adminDashboard():
    if  request.method == 'GET':
        if current_user.role != "admin":
            return redirect(url_for('home'))  
        user = current_user
        subjects = Subject.query.all()
        chapters = Chapter.query.all()
        users = User.query.all()
        quizzes = Quiz.query.all()

        subject_chapters = {}
        for subject in subjects:
            subject_chapters[subject] = [chapter for chapter in chapters if chapter.subject_id == subject.id]

        # Group quizzes by chapter
        chapter_quizzes = {}
        for chapter in chapters:
            chapter_quizzes[chapter] = [quiz for quiz in quizzes if quiz.chapter_id == chapter.id]


        draft_quiz = Quiz.query.filter(Quiz.status=="draft").all()
        scheduled_quiz = Quiz.query.filter(Quiz.status=="Scheduled").all()
        ongoing_quiz =  Quiz.query.filter(Quiz.status=="ongoing").all()
        completed_quiz = Quiz.query.filter(Quiz.status=="completed").all()


        return render_template('admin/dashboard.html', subjects=subjects,subject_chapters=subject_chapters,chapter_quizzes=chapter_quizzes,scheduled_quiz=scheduled_quiz,draft_quiz=draft_quiz,ongoing_quiz=ongoing_quiz,completed_quiz=completed_quiz)


def admin_Subject():
    if current_user.role != "admin":
        return redirect(url_for('home'))
    elif request.method == 'GET':
        subjects = Subject.query.all()
        chapters =Chapter.query.all()

        subject_chapters = {}
        for subject in subjects:
            subject_chapters[subject] = [chapter for chapter in chapters if chapter.subject_id == subject.id]

        return render_template('admin/admin_subject.html',subjects=subjects,subject_chapters =subject_chapters)  
    elif request.method == 'POST':
        action = request.form.get('action')

        if action == 'add_subject' :
            name = request.form.get('name')
            description = request.form.get('description')

            if name and description:
                new_subject = Subject(name=name, description =description)
                db.session.add(new_subject)
                db.session.commit()
                return redirect(url_for('admin_subject'))

            else:
                flash("Fill name and description fild properly.","error")
                return redirect(url_for('admin_subject'))    

        elif action == 'edit_subject' :
            subject_id = int(request.form.get('subject_id'))
            subject = Subject.query.get(subject_id)
            if not subject:
                flash("Invalid subject ID. The subject does not exist.", "danger")
                return redirect(url_for('admin_subject'))
            else :
                name = request.form.get('name')
                description = request.form.get('description')
                subject.name = name
                subject.description = description
                db.session.commit()
                return redirect(url_for('admin_subject'))

        elif action == 'delete_subject' :
            subject_id = int(request.form.get('subject_id'))
            name = request.form.get('name')
            subject = Subject.query.get(subject_id)

            if name == subject.name :
                db.session.delete(subject)
                db.session.commit()
                flash("Subject deleted successfully.", "success")
                return redirect(url_for('admin_subject'))

            else:
                flash("Subject name and ID does not match.Please try again.", "danger")
                return redirect(url_for('admin_subject'))    

def admin_Chapter(subject_id):
    if current_user.role != "admin":
        return redirect(url_for('home'))

    subject = Subject.query.filter_by(id=subject_id).first()

    if request.method == 'GET':
        
        chapters = Chapter.query.filter_by(subject_id=subject_id).all()
        subject_quizzes = []
        for chapter in chapters:
            draft_quizzes = Quiz.query.filter_by(chapter_id=chapter.id, status="draft").count()
            scheduled_quizzes = Quiz.query.filter_by(chapter_id=chapter.id, status="scheduled").count()
            ongoing_quizzes = Quiz.query.filter_by(chapter_id=chapter.id, status="ongoing").count()
            completed_quizzes = Quiz.query.filter_by(chapter_id=chapter.id, status="completed").count()
            subject_quizzes.append([chapter.id, draft_quizzes, scheduled_quizzes, ongoing_quizzes, completed_quizzes])

        return render_template('admin/admin_chapter.html', subject=subject, chapters=chapters, subject_quizzes=subject_quizzes)

    elif request.method == 'POST':
        action = request.form.get('action')

        if action == 'add_chapter':
            name = request.form.get('name')
            description = request.form.get('description')

            if name and description:
                new_chapter = Chapter(name=name, description=description, subject_id=subject.id)
                db.session.add(new_chapter)
                db.session.commit()
                return redirect(url_for('admin_chapter', subject_id=subject_id))
            else:
                flash("Fill name and description fields properly.", "error")
                return redirect(url_for('admin_chapter', subject_id=subject_id))

        elif action == 'edit_chapter':
            chapter_id = int(request.form.get('chapter_id'))
            chapter = Chapter.query.get(chapter_id)
            if not chapter:
                flash("Invalid chapter ID. The chapter does not exist.", "danger")
                return redirect(url_for('admin_chapter', subject_id=subject_id))
            else:
                name = request.form.get('name')
                description = request.form.get('description')
                chapter.name = name
                chapter.description = description
                db.session.commit()   
                return redirect(url_for('admin_chapter', subject_id=subject_id))

        elif action == 'delete_chapter':
            chapter_id = int(request.form.get('chapter_id'))
            name = request.form.get('name')
            chapter = Chapter.query.get(chapter_id)

            if name == chapter.name:
                db.session.delete(chapter)
                db.session.commit()
                flash("Chapter deleted successfully.", "success")
                return redirect(url_for('admin_chapter', subject_id=subject_id))
            else:
                flash("Chapter name and ID do not match. Please try again.", "danger")
                return redirect(url_for('admin_chapter', subject_id=subject_id))



def admin_Quiz(subject_id, chapter_id):
    if current_user.role != "admin":
        return redirect(url_for('home'))
    
    subject = Subject.query.get_or_404(subject_id)
    chapter = Chapter.query.get_or_404(chapter_id)

    if chapter.subject_id != subject.id :
        flash("Invalid input. Please check your data.", "error")
        return redirect(url_for('admin_chapter',subject_id=subject_id))

    elif request.method == 'GET':
        quizzes = Quiz.query.filter_by(chapter_id=chapter_id).order_by(db.case((Quiz.status == "draft", 1),(Quiz.status == "scheduled", 2),(Quiz.status == "ongoing", 3),(Quiz.status == "completed", 4)),Quiz.startline)
        
        return render_template('admin/admin_quiz.html',subject=subject,chapter=chapter,quizzes=quizzes)
    elif request.method == 'POST':
        quiz_id = request.form.get('quiz_id')
        
        if quiz_id:
            quiz_approve(quiz_id)
            flash("Quiz approval status updated successfully!", "success")
        else:
            flash("Quiz ID is missing!", "error")
            return redirect(url_for('admin_quiz', subject_id=subject_id, chapter_id=chapter_id))
        
        return redirect(url_for('admin_quiz', subject_id=subject_id, chapter_id=chapter_id))
    
    else :
        flash("Chapter name and ID does not match.Please try again.", "danger")
        return redirect(url_for('admin_quiz',subject_id= subject_id,chapter_id=chapter_id))

def manage_Quiz(subject_id, chapter_id):
    if current_user.role != "admin":
        return redirect(url_for('home'))
    
    subject = Subject.query.get_or_404(subject_id)
    chapter = Chapter.query.get_or_404(chapter_id)

    if chapter.subject_id != subject.id :
        flash("Invalid request. Please check your data.", "error")
        return redirect(url_for('admin_chapter',subject_id=subject_id))
    
    elif request.method == 'GET':
        quizzes = Quiz.query.filter_by(chapter_id=chapter_id).order_by(db.case((Quiz.status == "draft", 1),(Quiz.status == "scheduled", 2),(Quiz.status == "ongoing", 3),(Quiz.status == "completed", 4)),Quiz.startline).all()
        
        return render_template('admin/manage_quiz.html',subject_id=subject_id,chapter=chapter,quizzes=quizzes)
    
    elif request.method == 'POST':
        action = request.form.get('action')

        if action == 'add_quiz':
            name = request.form.get('name')
            description = request.form.get('description')
            startline = datetime.fromisoformat(request.form.get('startline'))
            deadline = datetime.fromisoformat(request.form.get('deadline'))
            duration = int(request.form.get('duration'))

            find = Quiz.query.filter_by(name =name,chapter_id=chapter_id).first()

            if find :
                flash(f"{name} Quiz already present. Please check","error")
                return redirect(url_for('manage_quiz',subject_id=subject_id,chapter_id=chapter_id))

            elif name and startline and deadline and duration and description:
                new_quiz = Quiz(
                    name=name,
                    description=description,
                    chapter_id=chapter_id,
                    startline=startline,
                    deadline=deadline,
                    duration=duration
                )
                db.session.add(new_quiz)
                db.session.commit()
                flash("Quiz added successfully!", "success")
                return redirect(url_for('manage_quiz',subject_id=subject_id,chapter_id=chapter_id))

            else:
                flash("Please provide all required fields.", "error")
                return redirect(url_for('manage_quiz',subject_id=subject_id,chapter_id=chapter_id))

        elif action == 'edit_quiz':
            quiz_id = int(request.form.get('quiz_id'))
            quiz = Quiz.query.get_or_404(quiz_id)
            name = request.form.get('name')
            description = request.form.get('description')
            startline = datetime.fromisoformat(request.form.get('startline'))  
            deadline = datetime.fromisoformat(request.form.get('deadline'))
            duration = int(request.form.get('duration'))
            print(startline)
            if quiz and quiz.chapter_id == chapter_id:

                if quiz.status == "completed":
                    new_quiz = Quiz(
                        name=name,
                        description=description,
                        chapter_id=chapter_id,
                        startline=startline,
                        deadline=deadline,
                        duration=duration
                    )
                    db.session.add(new_quiz)
                    db.session.commit()
                    return redirect(url_for('manage_quiz',subject_id=subject_id,chapter_id=chapter_id))

                elif quiz.status == "ongoing" and quiz.startline == startline :
                    quiz.name=name,
                    quiz.description=description
                    quiz.chapter_id=chapter_id
                    quiz.deadline=deadline
                    quiz.duration=duration
                    db.session.commit()
                    flash("Ongoing Quiz updated successfully!", "success")
                    return redirect(url_for('manage_quiz',subject_id=subject_id,chapter_id=chapter_id))

                elif quiz.status == "ongoing" and quiz.startline != startline :
                    new_quiz = Quiz(
                        name=name,
                        description=description,
                        chapter_id=chapter_id,
                        startline=startline,
                        deadline=deadline,
                        duration=duration
                    )
                    db.session.add(new_quiz)
                    db.session.commit()
                    flash("Quiz added successfully!", "success")
                    return redirect(url_for('manage_quiz',subject_id=subject_id,chapter_id=chapter_id))

                else:
                    print(startline)
                    quiz.name=name
                    quiz.description=description
                    quiz.chapter_id=chapter_id
                    quiz.startline= startline
                    quiz.deadline=deadline
                    quiz.duration=duration
                    quiz.create_date=datetime.now()
                    db.session.commit()
                    flash("Quiz updated successfully!", "success")
                    return redirect(url_for('manage_quiz',subject_id=subject_id,chapter_id=chapter_id))
                    
            else:
                flash("Invalid quiz ID or mismatch with the chapter.", "error")
                return redirect(url_for('manage_quiz',subject_id=subject_id,chapter_id=chapter_id))

        elif action == 'delete_quiz':
            quiz_id = int(request.form.get('quiz_id'))
            quiz = Quiz.query.get_or_404(quiz_id)
            name = request.form.get('name')

            if name == quiz.name :
                db.session.delete(quiz)
                db.session.commit()
                flash("Quiz deleted successfully.", "success")
                return redirect(url_for('manage_quiz',subject_id=subject_id,chapter_id=chapter_id))

            else:
                flash("Quiz name and ID does not match.Please try again.", "danger")
                return redirect(url_for('manage_quiz',subject_id = subject_id,chapter_id=chapter_id))    

            
def manage_Question(subject_id,chapter_id,quiz_id):
    if current_user.role != "admin":
        return redirect(url_for('home'))
    
    subject = Subject.query.get_or_404(subject_id)
    chapter = Chapter.query.get_or_404(chapter_id)
    quiz = Quiz.query.get_or_404(quiz_id)

    if subject.id != chapter.subject_id and quiz.chapter_id != chapter_id:
        flash("Invalid request. Please check your data.", "error")
        return redirect(url_for('admin_chapter',subject_id=subject_id))
    
    elif request.method == 'GET':
        questions = Questions.query.filter_by(quiz_id=quiz.id).all()
        total_marks = get_total_marks(quiz_id)
        quiz.total_score = total_marks
        db.session.commit()


        return render_template('admin/manage_question.html',questions=questions,total_marks=total_marks,chapter=chapter,subject=subject,quiz=quiz)
    
    elif request.method == 'POST':
        action = request.form.get('action')

        if action == 'add_question' :
            text = request.form.get('text')
           
            option1 = request.form.get('option1')
            option2 = request.form.get('option2')
            option3 = request.form.get('option3')
            option4 = request.form.get('option4')
            correct_option = int(request.form.get('correct_option'))
            marks = int(request.form.get('marks'))

            if quiz.status == 'draft' or quiz.status == 'scheduled' :
                if text and option1 and option2 and option3 and option4 and correct_option and marks :
                    new_question = Questions(
                        text = text,
                        quiz_id = quiz_id,
                        option1 = option1,
                        option2 = option2,
                        option3 = option3,
                        option4 = option4,
                        correct_option = correct_option,
                        marks = marks
                    )
                    db.session.add(new_question)
                    db.session.commit()
                    flash("Quiz added successfully!", "success")
                    return redirect(url_for('manage_question',subject_id=subject_id,chapter_id=chapter_id,quiz_id=quiz_id)) 

                else:
                    flash("Please provide all required fields.", "error")   
                    return redirect(url_for('manage_question',subject_id=subject_id,chapter_id=chapter_id,quiz_id=quiz_id)) 

            elif quiz.status == 'ongoing':
                confirmed = request.json.get('confirmed')
                if confirmed:
                    try:
                        if text and option1 and option2 and option3 and option4 and correct_option and marks :
                            new_question = Questions(
                                text = text,
                                quiz_id = quiz_id,
                                option1 = option1,
                                option2 = option2,
                                option3 = option3,
                                option4 = option4,
                                correct_option = correct_option,
                                marks = marks
                            )
                            db.session.add(new_question)
                            db.session.commit()
                            flash("Quiz added successfully!", "success")
                            return redirect(url_for('manage_question',subject_id=subject_id,chapter_id=chapter_id,quiz_id=quiz_id)) 


                        else:
                            flash("Please provide all required fields.", "error")   
                            return redirect(url_for('manage_question',subject_id=subject_id,chapter_id=chapter_id,quiz_id=quiz_id)) 

                    except Exception as e:
                        flash(f"An error occurred: {e}", "error") 
                        return redirect(url_for('manage_question',subject_id=subject_id,chapter_id=chapter_id,quiz_id=quiz_id)) 
   

                else:
                    flash("Operation canceled .", "warning")
                    return redirect(url_for('manage_question',subject_id=subject_id,chapter_id=chapter_id,quiz_id=quiz_id)) 
                
                return jsonify({"success": True})
            
            else:
                flash("Question can not be added in completed quiz.","error")
                return redirect(url_for('manage_question',subject_id=subject_id,chapter_id=chapter_id,quiz_id=quiz_id))


        elif action == 'edit_question':
            question_id = int(request.form.get('question_id'))
            question = Questions.query.get_or_404(question_id)
            text = request.form.get('text')
            option1 = request.form.get('option1')
            option2 = request.form.get('option2')
            option3 = request.form.get('option3')
            option4 = request.form.get('option4')
            correct_option = request.form.get('correct_option')
            marks = request.form.get('marks')
            if question and question.quiz_id == quiz_id:
                if text:
                    question.text = text
                if option1:
                    question.option1 = option1
                if option2:
                    question.option2 = option2
                if option3:
                    question.option3 = option3
                if option4:
                    question.option4 = option4
                if correct_option:
                    question.correct_option = correct_option
                if marks:  
                    question.marks = marks   

                if quiz.status == 'draft' or quiz.status == 'scheduled':
                    db.session.commit()
                    flash("Question is edited successfully.","success")
                    return redirect(url_for('manage_question',subject_id=subject_id,chapter_id=chapter_id,quiz_id=quiz_id)) 


                elif quiz.status == 'ongoing' :
                    confirmed = request.json.get('confirmed')
                    if confirmed:
                        db.session.commit()
                        flash("Question is edited successfully.","success")
                    else:
                        return redirect(url_for('manage_question',subject_id=subject_id,chapter_id=chapter_id,quiz_id=quiz_id))
                    
                else:
                    flash("Questions in completed quiz can not be changed","error")
                    return redirect(url_for('manage_question',subject_id=subject_id,chapter_id=chapter_id,quiz_id=quiz_id))
            else:
                flash("Invalid request. Please check your data.", "error")
                return redirect(url_for('manage_quiz',subject_id=subject_id,chapter_id=chapter_id))

        elif action == 'delete_question':
            question_id = int(request.form.get('question_id'))
            question = Questions.query.get_or_404(question_id)
            if question and question.quiz_id == quiz_id:
                if quiz.status == 'draft' or quiz.status == 'schedlued':
                    db.session.delete(question)
                    db.session.commit()
                    flash("Question deleted successfully.", "success")
                    return redirect(url_for('manage_question',subject_id=subject_id,chapter_id=chapter_id,quiz_id=quiz_id)) 


                elif quiz.status == 'ongoing' :
                    confirmed = request.json.get('confirmed')
                    if confirmed:
                        db.session.delete(question)
                        db.session.commit()
                        flash("Question deleted successfully.", "success")
                        return redirect(url_for('manage_question',subject_id=subject_id,chapter_id=chapter_id,quiz_id=quiz_id)) 


                    else:
                        return redirect(url_for('manage_question',subject_id=subject_id,chapter_id=chapter_id,quiz_id=quiz_id))    
                    
                else:
                    flash("Questions in completed quiz can not be deleted","error")
                    return redirect(url_for('manage_question',subject_id=subject_id,chapter_id=chapter_id,quiz_id=quiz_id))    
                
            else:
                flash("Invalid request. Please check your data.", "error")
                return redirect(url_for('manage_quiz',subject_id=subject_id,chapter_id=chapter_id))
        else:
            flash("Invalid request. Please check your data.", "error")
            return redirect(url_for('manage_quiz',subject_id=subject_id,chapter_id=chapter_id))
    else:
            flash("Invalid request. Please check your data.", "error")
            return redirect(url_for('manage_quiz',subject_id=subject_id,chapter_id=chapter_id))

#need to check
def index_Quiz(subject_id,chapter_id,quiz_id):
    if current_user.role != "admin":
        return redirect(url_for('home'))
    
    subject = Subject.query.get_or_404(subject_id)
    chapter = Chapter.query.get_or_404(chapter_id)
    quiz = Quiz.query.get_or_404(quiz_id)

    if subject.id != chapter.subject_id or quiz.chapter_id != chapter.id:
        flash("Invalid request. Please check your data.", "error")
        return redirect(url_for('admin_chapter', subject_id=subject_id))
    
    if request.method == 'GET':
        questions = Questions.query.filter_by(quiz_id=quiz_id).all()
        total_marks = get_total_marks(quiz_id)
        return render_template('admin/index_quiz.html', questions=questions, total_marks=total_marks, chapter=chapter, subject=subject, quiz=quiz)

    elif request.method == 'POST':
        questions = Questions.query.filter_by(quiz_id=quiz_id).all()
        total_marks = get_total_marks(quiz_id)
        
        for question in questions:
            question_index = request.form.get(f'index_{question.id}')
            if question_index:
                question.index = int(question_index)

        db.session.commit()
        flash("Question order saved successfully!", "success")
        return redirect(url_for('index_quiz', subject_id=subject_id, chapter_id=chapter_id, quiz_id=quiz_id))
    
    return redirect(url_for('index_quiz', subject_id=subject_id, chapter_id=chapter_id, quiz_id=quiz_id))
    

def userCheck():
    if  request.method == 'GET':
        if current_user.role != "admin":
            return redirect(url_for('home'))
        else:
            users = User.query.all()
            return render_template('admin/user_allow.html',users=users)   
    elif  request.method == 'POST': 
        action = request.form.get('action')
        user_id = request.form.get('user_id')
        search_term = request.form.get('search_term')
        search_type = request.form.get('search_type')

        if action == 'allow':
            if user_id:
                user_allow(user_id)
                flash("User status updated successfully!", "success")
            else:
                flash("user ID is missing!", "error")
                return redirect(url_for('usercheck'))
            
            return redirect(url_for('usercheck'))
        
        elif action == 'cancel':
            if user_id:
                user_allow(user_id)
                flash("User status updated successfully!", "success")
            else:
                flash("user ID is missing!", "error")
                return redirect(url_for('usercheck'))
            
            return redirect(url_for('usercheck'))
        
        elif action ==  'delete':
            if user_id:
                user = User.query.get(user_id)
                db.session.delete(user)
                db.session.commit()
                flash(f"user{user_id} deleted successfully.", "success")

        elif action == 'search' and search_term:
            users = User.query.all()

            if search_type == 'email':
                    search_user = User.query.filter(User.email.ilike(f'%{search_term}%')).all()
                    if search_user:
                        flash(f"Users with email '{search_term}' found.", "success")
                        return render_template('admin/user_allow.html', users=users, search_user=search_user)  
                    else:
                        flash(f"No users found with email '{search_term}'.", "error")
                        return redirect(url_for('usercheck'))
            elif search_type == 'id':
                search_id = int(search_term)
                search_user = User.query.filter_by(id=search_id).all() 
                if search_user:
                    flash(f"Users with name '{search_term}' found.", "success")
                    return render_template('admin/user_allow.html', users=users, search_user=search_user)  
                else:
                    flash(f"No users found with name '{search_term}'.", "error")
                    return redirect(url_for('usercheck'))   
            else:
                flash("Please enter a search term!", "error")
                return redirect(url_for('usercheck'))

        else :
            flash("Invalid action!", "error")
        users = User.query.all()
        return redirect(url_for('usercheck', users=users))
        
    else :
            return redirect(url_for('admin_dashboard'))    



    
    
    










        


















      


     


