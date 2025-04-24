from flask import Flask , render_template , request ,redirect, url_for,flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager,login_user,login_required,logout_user,current_user
from controllers.model import db,User,Subject,Chapter,Quiz,Questions,Scores,UserLogin,UserAnswer
from controllers.function import get_total_score,subject_Scoreboard,leader_Board,Scoreboard,update_score

def userDashboard():
    if request.method == 'GET':
        if current_user.role != "user":
            return redirect(url_for('home'))
        
        user_id = current_user.id.split("_")[1]
        subjects = Subject.query.all()
        chapters = Chapter.query.all()
        quizzes = Quiz.query.all()
        total_score = get_total_score(user_id)

        subject_chapters = {}
        for subject in subjects:
            subject_chapters[subject] = [chapter for chapter in chapters if chapter.subject_id == subject.id]

            # Group quizzes by chapter
        chapter_quizzes = {}
        for chapter in chapters:
            chapter_quizzes[chapter] = [quiz for quiz in quizzes if quiz.chapter_id == chapter.id]

        upcoming_quiz =  Quiz.query.filter_by(status="scheduled").all()    

        ongoing_quiz =  Quiz.query.filter_by(status="ongoing").all()
        count_ongoing_quiz = len(ongoing_quiz)
        count_upcoming_quiz = len(upcoming_quiz)
    
        return render_template('user/dashboard.html',count_ongoing_quiz=count_ongoing_quiz,ongoing_quiz=ongoing_quiz,subjects=subjects,subject_chapters=subject_chapters,chapter_quizzes=chapter_quizzes,upcoming_quiz=upcoming_quiz,
                            total_score=total_score,count_upcoming_quiz=count_upcoming_quiz)
    
def user_Subject():
    if current_user.role != "user":
        return redirect(url_for('home'))
    if request.method == 'GET':
        subjects = Subject.query.all()
        chapters =Chapter.query.all()
        leaderboard= Scoreboard()

        subject_chapters = {}
        for subject in subjects:
            subject_chapters[subject] = [chapter for chapter in chapters if chapter.subject_id == subject.id]

        return render_template('user/user_subject.html',subjects=subjects,subject_chapters =subject_chapters,leaderboard=leaderboard)
    else :
        flash("An error occurred. Please try again.", "error")
        return redirect(url_for('user_dashboard'))     

def user_Chapter(subject_id):
    if current_user.role != "user":
        return redirect(url_for('home'))
    
    subject = Subject.query.get_or_404(subject_id)
    
    if request.method == 'GET':
        chapters = Chapter.query.filter_by(subject_id = subject_id).all()

        subject_quizzes = {}
        for chapter in chapters:
            scheduled_quizzes = Quiz.query.filter_by(chapter_id = chapter.id,status = "scheduled").all()
            ongoing_quizzes = Quiz.query.filter_by(chapter_id = chapter.id,status = "ongoing").all()
            completed_quizzes = Quiz.query.filter_by(chapter_id = chapter.id, status = "completed").all()
            
            subject_quizzes[chapter.id] = [scheduled_quizzes,ongoing_quizzes,completed_quizzes]
        return render_template('user/user_chapter.html',subject=subject,chapters =chapters ,subject_quizzes=subject_quizzes)
    
    else :
        flash("An error occurred. Please try again.", "error")
        return redirect(url_for('user_subject'))
    
def user_Quiz(subject_id, chapter_id):
    if current_user.role != "user":
        return redirect(url_for('home'))
    
    subject = Subject.query.get_or_404(subject_id)
    chapter = Chapter.query.get_or_404(chapter_id)

    if chapter.subject_id != subject.id :
        flash("Invalid input. Please check your data.", "error")
        return redirect(url_for('user_chapter',subject_id=subject_id))

    elif request.method == 'GET':
        quizzes = Quiz.query.filter_by(chapter_id=chapter_id).order_by(db.case((Quiz.status == "ongoing", 1),(Quiz.status == "scheduled", 2),(Quiz.status == "completed", 3)),Quiz.startline)
        return render_template('user/user_quiz.html',subject=subject,chapter=chapter,quizzes=quizzes)
    
    else :
        flash("Chapter name and ID does not match.Please try again.", "danger")
        return redirect(url_for('user_quiz',subject_id= subject_id,chapter_id=chapter_id))
    
def quiz_Detail(subject_id, chapter_id,quiz_id):
    if current_user.role != "user":
        return redirect(url_for('home'))
    
    subject = Subject.query.get_or_404(subject_id)
    chapter = Chapter.query.get_or_404(chapter_id)
    quiz = Quiz.query.get_or_404(quiz_id)

    if chapter.subject_id != subject.id and quiz.chapter_id == chapter.id:
        flash("Invalid input. Please check your data.", "error")
        return redirect(url_for('user_quiz',subject_id=subject_id,chapter_id=chapter_id))
    
    elif request.method == 'GET':
        if quiz.status == 'draft':
            flash("Invalid input. Please check your data.", "error")
            return redirect(url_for('user_quiz',subject_id=subject_id,chapter_id=chapter_id))
        else:

            question=Questions.query.filter_by(quiz_id=quiz.id).count()
            return render_template('user/quiz_detail.html',subject=subject,chapter=chapter,quiz=quiz,question=question)
        
    else :
        flash("Chapter name and ID does not match.Please try again.", "danger")
        return redirect(url_for('quiz_detail',subject_id= subject_id,chapter_id=chapter_id,quiz_id=quiz_id))    
        
def quiz_Test(subject_id, chapter_id,quiz_id):
    if current_user.role != "user":
        return redirect(url_for('home')) 
    user_id = current_user.id.split("_")[1]
    user = User.query.filter_by(id=user_id).first()

    if user.allow:
    
        subject = Subject.query.get_or_404(subject_id)
        chapter = Chapter.query.get_or_404(chapter_id)
        quiz = Quiz.query.get_or_404(quiz_id)
        user_answer = UserAnswer.query.filter_by(user_id=user_id, quiz_id=quiz_id).first()

        if chapter.subject_id != subject.id and quiz.chapter_id == chapter.id:
            flash("Invalid input. Please check your data.", "error")
            return redirect(url_for('user_quiz',subject_id=subject_id,chapter_id=chapter_id))
        
        elif request.method == 'GET':
            if quiz.status == 'draft':
                flash("Invalid input. Please check your data.", "error")
                return redirect(url_for('user_quiz',subject_id=subject_id,chapter_id=chapter_id))
            
            elif quiz.status == 'scheduled':
                flash(f"The test is scheduled to begin shortly. Please be patient and check back at {quiz.startline}.")
                return redirect(url_for('quiz_test',subject_id=subject_id,chapter_id=chapter_id))
            
            elif quiz.status == 'ongoing':
                if not  user_answer:
                    questions = Questions.query.filter_by(quiz_id=quiz.id).order_by(Questions.index).all()  
                    return render_template('user/quiz_test.html', quiz=quiz,questions=questions)
                else:
                    flash("You have completed the quiz.Wait for deadline to acsess again","error")
                    return redirect(url_for('user_quiz',subject_id=subject_id,chapter_id=chapter_id))

            elif quiz.status == 'completed':
                if not user_answer:
                    user_answer = None
                    answers = []
                else:    
                    answers = user_answer.selected_answer.split(',')

                total_score = 0
                results = []
                for idx, question in enumerate(Questions.query.filter_by(quiz_id=quiz_id).order_by(Questions.index).all()):
                    selected_answer = answers[idx] if idx < len(answers) else '0'
                    is_correct = int(selected_answer) == question.correct_option
                    if is_correct:
                        total_score += question.marks

                    results.append({
                        'question_text': question.text,
                        'marks': question.marks,
                        'options':[question.option1,question.option2,question.option3,question.option4],
                        'correct_option': question.correct_option,
                        'selected_answer': selected_answer,
                        'is_correct': is_correct
                    })
                
                return render_template('user/quiz_completed.html', quiz=quiz, subject=subject, chapter=chapter, results=results, total_score=total_score)
            
            
            else:
                flash("Someting went wrong.","error")
                return redirect(url_for('user_quiz',subject_id=subject_id,chapter_id=chapter_id))
            
        elif request.method == 'POST':  
            questions = Questions.query.filter_by(quiz_id=quiz.id).order_by(Questions.index).all()
            user_id = current_user.id.split("_")[1]
            answers = []
            total_score = 0

            for question in questions:
                user_answer = request.form.get(f'question_{question.id}', '0')
                answers.append(user_answer)
                if int(user_answer) == question.correct_option:
                    total_score += question.marks

            total_score = round((total_score / quiz.total_score) * 100)
            user_record = UserAnswer(
                quiz_id=quiz_id,
                user_id=user_id,
                selected_answer=','.join(answers),
                score=total_score
            )
            db.session.add(user_record)
            db.session.commit()
            update_score(user_id,quiz_id)

            return redirect(url_for('quiz_detail', subject_id=subject_id, chapter_id=chapter_id, quiz_id=quiz_id))

    else:
        flash("You do not access to this page.", "error")
        return redirect(url_for('quiz_detail', subject_id=subject_id, chapter_id=chapter_id, quiz_id=quiz_id))