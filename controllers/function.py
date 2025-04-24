
from sqlalchemy import func
from controllers.model import db,User,Admin,Subject,Chapter,Quiz,Questions,Scores,UserLogin,UserAnswer
from controllers.login import Login,Logout,current_user
from flask import Flask , render_template , request ,redirect, url_for,flash,jsonify
import os
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
import base64
import matplotlib
matplotlib.use('Agg')



static_dir = os.path.join(os.getcwd(), 'static')
if not os.path.exists(static_dir):
    os.makedirs(static_dir)


def create_pie_chart(data, labels, title, filename):
    fig, ax = plt.subplots()
    ax.pie(data, labels=labels, autopct='%1.1f%%', startangle=90, colors=['#ff9999', '#66b3ff', '#99ff99'])
    ax.axis('equal')  
    ax.set_title(title)
    plt.savefig(os.path.join('static', filename))
    plt.close()

def create_stacked_bar_chart(correct_answers_count, incorrect_answers_count, questions, filename):
    fig, ax = plt.subplots()
    ax.bar([q.id for q in questions], correct_answers_count, label='Correct', color='green')
    ax.bar([q.id for q in questions], incorrect_answers_count, label='Incorrect', bottom=correct_answers_count, color='red')
    ax.set_xlabel('Questions')
    ax.set_ylabel('Number of Answers')
    ax.set_title('Correct/Incorrect Answers Per Question')
    ax.legend()

    plt.tight_layout()  # Adjust layout to prevent clipping of tick labels
    plt.savefig(os.path.join('static', filename))
    plt.close()

def create_stacked_bar_chart(correct_answers_count, incorrect_answers_count, questions, filename):

    fig, ax = plt.subplots()

    x_pos = [q.id for q in questions]
    
    ax.bar(x_pos, correct_answers_count, label='Correct', color='green', width=0.4, align='center')
    ax.bar(x_pos, incorrect_answers_count, label='Incorrect', color='red', width=0.4, align='center', bottom=correct_answers_count)

    ax.set_xlabel('Questions')
    ax.set_ylabel('Number of Answers')
    ax.set_title('Correct/Incorrect Answers Per Question')
    ax.legend()

    plt.tight_layout()
    plt.savefig(os.path.join('static', filename))
    plt.close()







def get_total_score(user_id):
    total_score = db.session.query(func.sum(Scores.score)).filter(Scores.user_id == user_id).scalar()
    return total_score if total_score is not None else 0


def get_total_marks(quiz_id):
    total_marks = db.session.query(func.sum(Questions.marks)).filter(Questions.quiz_id == quiz_id).scalar()
    return total_marks if total_marks is not None else 0

def Scoreboard():
    leaderboard = db.session.query(
            User.id,
            User.name,
            User.email,
            func.count(Scores.quiz_id).label('quizzes_attempted'),
            func.sum(Scores.score).label('scored'),
            (func.count(Scores.score) * 100).label('total_score')
        ).join(Scores, Scores.user_id == User.id) \
        .join(Quiz, Scores.quiz_id == Quiz.id) \
        .group_by(User.id) \
        .order_by(func.sum(Scores.score).desc()) \
        .all()
    
    return leaderboard
def user_scoreboard():
    user_id = current_user.id.split("_")[1]
    user_board = db.session.query(
            User.id,
            User.name,
            User.email,
            func.count(Scores.quiz_id).label('quizzes_attempted'),
            func.sum(Scores.score).label('scored'),
            (func.count(Scores.score) * 100).label('total_score')
        ).join(Scores, Scores.user_id == User.id) \
        .join(Quiz, Scores.quiz_id == Quiz.id) \
        .filter(User.id == user_id) \
        .group_by(User.id) \
        .order_by(func.sum(Scores.score).desc()) \
        .all()
    return user_board



def subject_Scoreboard(subject_name):
    subject = Subject.query.filter_by(name=subject_name).first_or_404()
    chapters = Chapter.query.filter_by(subject_id=subject.id).all()
    chapter_ids = [chapter.id for chapter in chapters]
    
    leaderboard = db.session.query(
        User.id,
        User.name,
        User.email,
        func.count(Scores.quiz_id).label('quizzes_attempted'),
        func.sum(Scores.score).label('scored'),
        (func.count(Scores.score) * 100).label('total_score')
    ).join(Scores, Scores.user_id == User.id) \
     .join(Quiz, Scores.quiz_id == Quiz.id) \
     .filter(Quiz.chapter_id.in_(chapter_ids)) \
     .group_by(User.id) \
     .order_by(func.sum(Scores.score).desc()) \
     .all()
    
    return leaderboard
def user_subboard(subject_name):
    user_id = current_user.id.split("_")[1]
    subject = Subject.query.filter_by(name=subject_name).first_or_404()
    chapters = Chapter.query.filter_by(subject_id=subject.id).all()
    chapter_ids = [chapter.id for chapter in chapters]
    
    user_board = db.session.query(
        User.id,
        User.name,
        User.email,
        func.count(Scores.quiz_id).label('quizzes_attempted'),
        func.sum(Scores.score).label('scored'),
        (func.count(Scores.score) * 100).label('total_score')
    ).join(Scores, Scores.user_id == User.id) \
     .join(Quiz, Scores.quiz_id == Quiz.id) \
     .filter(Quiz.chapter_id.in_(chapter_ids)) \
     .filter(User.id == user_id) \
     .group_by(User.id) \
     .order_by(func.sum(Scores.score).desc()) \
     .all()
    
    return user_board

def chapter_Scoreboard(subject_name, chapter_name):
    subject = Subject.query.filter_by(name=subject_name).first_or_404()
    chapter = Chapter.query.filter_by(name=chapter_name, subject_id=subject.id).first_or_404()

    
    leaderboard = db.session.query(
        User.id,
        User.name,
        User.email,
        func.count(Scores.quiz_id).label('quizzes_attempted'),
        func.sum(Scores.score).label('scored'),
        (func.count(Scores.score) * 100).label('total_score')
    ).join(Scores, Scores.user_id == User.id) \
     .join(Quiz, Scores.quiz_id == Quiz.id) \
     .filter(Quiz.chapter_id == chapter.id) \
     .group_by(User.id) \
     .order_by(func.sum(Scores.score).desc()) \
     .all()
    
    

    return leaderboard
def user_chapboard(subject_name, chapter_name):
    user_id = current_user.id.split("_")[1]
    subject = Subject.query.filter_by(name=subject_name).first_or_404()
    chapter = Chapter.query.filter_by(name=chapter_name, subject_id=subject.id).first_or_404()
    
    user_board = db.session.query(
        User.id,
        User.name,
        User.email,
        func.count(Scores.quiz_id).label('quizzes_attempted'),
        func.sum(Scores.score).label('scored'),
        (func.count(Scores.score) * 100).label('total_score')
    ).join(Scores, Scores.user_id == User.id) \
     .join(Quiz, Scores.quiz_id == Quiz.id) \
     .filter(Quiz.chapter_id == chapter.id) \
     .filter(User.id == user_id) \
     .group_by(User.id) \
     .order_by(func.sum(Scores.score).desc()) \
     .all()

    return user_board


def quiz_Scoreboard(subject_name, chapter_name, quiz_name):
    subject = Subject.query.filter_by(name=subject_name).first_or_404()
    chapter = Chapter.query.filter_by(name=chapter_name, subject_id=subject.id).first_or_404()
    quiz = Quiz.query.filter_by(name=quiz_name, chapter_id=chapter.id).first_or_404()

    leaderboard = db.session.query(
        User.id,
        User.name,
        User.email,
        1,
        (Scores.score).label('total_score'),
        100
    ).join(Scores, Scores.user_id == User.id) \
    .join(Quiz, Scores.quiz_id == quiz.id) \
    .filter(Scores.quiz_id == quiz.id) \
    .group_by(User.id) \
    .order_by(func.sum(Scores.score).desc()) \
    .all()
    
    return leaderboard
def user_quizboard(subject_name, chapter_name, quiz_name):
    user_id = current_user.id.split("_")[1]
    subject = Subject.query.filter_by(name=subject_name).first_or_404()
    chapter = Chapter.query.filter_by(name=chapter_name, subject_id=subject.id).first_or_404()
    quiz = Quiz.query.filter_by(name=quiz_name, chapter_id=chapter.id).first_or_404()

    user_board = db.session.query(
        User.id,
        User.name,
        User.email,
        1,  
        (db.session.query(Scores.score)
            .filter(Scores.user_id == user_id, Scores.quiz_id == quiz.id)
            .first()[0] if db.session.query(Scores.score)
                         .filter(Scores.user_id == user_id, Scores.quiz_id == quiz.id)
                         .first() else 0),
        100 ).filter(Scores.quiz_id == quiz.id) \
    .filter(Scores.user_id == user_id) \
    .join(Scores, Scores.user_id == User.id) \
    .all()

    return user_board


def leader_Board():

    if request.method == 'GET':
        leaderboard = Scoreboard()
        user_board = user_scoreboard()
        subjects = Subject.query.all()
        chapters = Chapter.query.all()
        quizzes = Quiz.query.all()
        
        return render_template('leaderboard/leader_board.html', 
                               subjects=subjects, 
                               chapters=chapters, 
                               quizzes=quizzes,
                               user_board=user_board, 
                               leaderboard=leaderboard)
    
    elif request.method == 'POST':
        subject_name = request.form.get('subject')
        chapter_name = request.form.get('chapter')
        quiz_name = request.form.get('quiz')

        subjects = Subject.query.all()
        chapters = []
        quizzes = []
        leaderboard = None

        try:
            if subject_name:
                subject = Subject.query.filter_by(name=subject_name).first()
                if not subject:
                    flash("Subject not found.", "error")
                    return redirect(url_for('leader_board'))

                chapters = Chapter.query.filter_by(subject_id=subject.id).all()

                if chapter_name:
                    chapter = Chapter.query.filter_by(name=chapter_name, subject_id=subject.id).first()
                    if not chapter:
                        flash("Chapter not found.", "error")
                        return redirect(url_for('leader_board'))

                    quizzes = Quiz.query.filter_by(chapter_id=chapter.id).all()

                    if quiz_name:
                        quiz = Quiz.query.filter_by(chapter_id=chapter.id, name=quiz_name).first()
                        if not quiz:
                            flash("Quiz not found.", "error")
                            return redirect(url_for('leader_board'))

                        leaderboard = quiz_Scoreboard(subject_name, chapter_name, quiz_name)
                        user_board = user_quizboard(subject_name, chapter_name, quiz_name)

                        total_students = User.query.filter_by(allow=True).count()
                        students_given_quiz = Scores.query.filter_by(quiz_id=quiz.id).count()
                        students_not_given_quiz = total_students - students_given_quiz

                        pie_chart_1_filename = 'pie_chart_given_quiz.png'
                        create_pie_chart([students_given_quiz, students_not_given_quiz], 
                                         ['Given Quiz', 'Not Given Quiz'], 
                                         'Users Who Have Given the Quiz', 
                                         pie_chart_1_filename)

                        score_ranges = {'0-50%': 0, '51-70%': 0, '71-100%': 0}
                        for entry in leaderboard:
                            score = entry.total_score
                            if score <= 50:
                                score_ranges['0-50%'] += 1
                            elif score <= 70:
                                score_ranges['51-70%'] += 1
                            else:
                                score_ranges['71-100%'] += 1

                        pie_chart_2_filename = 'pie_chart_score_distribution.png'
                        create_pie_chart(list(score_ranges.values()), 
                                         list(score_ranges.keys()), 
                                         'Percentage Count of Students Based on Score', 
                                         pie_chart_2_filename)

                        questions = Questions.query.filter_by(quiz_id=quiz.id).order_by(Questions.index).all()
                        correct_answers_count = [0] * len(questions)
                        incorrect_answers_count = [0] * len(questions)

                        for entry in leaderboard:
                            user_id = entry[0]
                            user_answers = UserAnswer.query.filter_by(user_id=user_id, quiz_id=quiz.id).first()
                            answers = user_answers.selected_answer.split(',')

                            for idx, question in enumerate(Questions.query.filter_by(quiz_id=quiz.id).order_by(Questions.index).all()):
                                selected_answer = answers[idx] if idx < len(answers) else '0'
                                is_correct = int(selected_answer) == question.correct_option
                                if is_correct:
                                    correct_answers_count[idx] += 1
                                else:
                                    incorrect_answers_count[idx] += 1

                        stacked_bar_chart_filename = 'stacked_bar_chart_correct_incorrect_answers.png'
                        create_stacked_bar_chart(correct_answers_count, 
                                                incorrect_answers_count, 
                                                questions, 
                                                stacked_bar_chart_filename)

                        return render_template('leaderboard/leader_board.html', 
                                               subjects=subjects, 
                                               chapters=chapters, 
                                               quizzes=quizzes, 
                                               user_board=user_board,
                                               leaderboard=leaderboard,
                                               selected_subject=subject.name, 
                                               selected_chapter=chapter.name, 
                                               selected_quiz=quiz.name,
                                               pie_chart_1=pie_chart_1_filename, 
                                               pie_chart_2=pie_chart_2_filename, 
                                               stacked_bar_chart_filename=stacked_bar_chart_filename)

                    else:
                        leaderboard = chapter_Scoreboard(subject_name, chapter_name)
                        user_board = user_chapboard(subject_name, chapter_name)
                        return render_template('leaderboard/leader_board.html', 
                                               subjects=subjects, 
                                               chapters=chapters, 
                                               quizzes=quizzes, 
                                               user_board=user_board,
                                               leaderboard=leaderboard,
                                               leaderboard_chart=None,
                                               selected_subject=subject.name, 
                                               selected_chapter=chapter.name, 
                                               selected_quiz=None)
                else:
                    leaderboard = subject_Scoreboard(subject_name)
                    user_board = user_subboard(subject_name)
                    return render_template('leaderboard/leader_board.html', 
                                           subjects=subjects, 
                                           chapters=chapters, 
                                           quizzes=quizzes,  
                                           user_board=user_board,
                                           leaderboard=leaderboard,
                                           leaderboard_chart=None,
                                           selected_subject=subject.name, 
                                           selected_chapter=None,  
                                           selected_quiz=None)
            else:
                flash("Please select a subject.", "error")
                return redirect(url_for('leader_board'))

        except Exception as e:
            leaderboard = Scoreboard()
            user_board = user_scoreboard()
            flash(f"An error occurred: {str(e)}", "error")
            return render_template('leaderboard/leader_board.html', 
                                   subjects=subjects, 
                                   chapters=chapters, 
                                   quizzes=quizzes,
                                   user_board=user_board,
                                   leaderboard=leaderboard,
                                   selected_subject=subject_name, 
                                   selected_chapter=chapter_name, 
                                   selected_quiz=quiz_name)

    else:
        return "Method Not Allowed", 405

    
          



def quiz_approve(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if quiz:
        quiz.approved = not quiz.approved
        db.session.commit()
        return quiz
    else:
        None



def update_score(user_id, quiz_id):
    user_answers = UserAnswer.query.filter_by(user_id=user_id, quiz_id=quiz_id).first()
    if not user_answers:
        print("No answers found for the user.")
        return None
    
    total_score = user_answers.score


    score_entry = Scores.query.filter_by(user_id=user_id, quiz_id=quiz_id).first()
    if score_entry:
        print(f"Score to {total_score}")
        return f"Quiz is attempted by {user_id}"
    else:
        score_entry = Scores(user_id=user_id, quiz_id=quiz_id, score=total_score, status="Attempted")
        db.session.add(score_entry)
    
    db.session.commit()
    print(f"Score updated to {total_score}")
    return f"Score updated to {total_score}"


def user_allow(user_id):
    user=User.query.get(user_id)
    if user:
        user.allow = not user.allow
        db.session.commit()
        return user
    else:
        None









