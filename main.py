from flask import Flask, render_template, redirect, abort, request
from forms.user import RegisterForm
from forms.loginform import LoginForm
from forms.depform import DepartmentForm
from forms.news import NewsForm
from forms.jobform import JobsForm
from data import db_session
from data.users import User
from data.news import News
from data.departments import Department
from data.jobs import Jobs
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, BooleanField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)
'''Hri-Q3p-vgU-rf9'''
'''password: cap, coock, life, chemist'''
def main():
    db_session.global_init('db/mars_explorer.db')
    db_sess = db_session.create_session()
    @app.route("/")
    def index():
        data = zip(db_sess.query(Jobs).all(), db_sess.query(User).all())
        return render_template("index.html", data=data)
    @app.route("/departments")
    def index_dep():
        data = db_sess.query(Department).all()
        return render_template("index_dep.html", data=data)
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            user = db_sess.query(User).filter(User.email == form.email.data).first()
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                return redirect("/")
            return render_template('login.html',
                                   message="Неправильный логин или пароль",
                                   form=form)
        return render_template('login.html', title='Авторизация', form=form)
    
    @app.route('/register', methods=['GET', 'POST'])
    def reqister():
        form = RegisterForm()
        if form.validate_on_submit():
            if form.password.data != form.password_again.data:
                return render_template('register.html', title='Регистрация',
                                       form=form,
                                       message="Пароли не совпадают")
            db_sess = db_session.create_session()
            if db_sess.query(User).filter(User.email == form.email.data).first():
                return render_template('register.html', title='Регистрация',
                                       form=form,
                                       message="Такой пользователь уже есть")
            user = User(
                name=form.name.data,
                surname=form.surname.data,
                age=form.age.data,
                position=form.position.data,
                speciality=form.speciality.data,
                address=form.address.data,
                email=form.email.data,
            )
            user.set_password(form.password.data)
            
            db_sess.add(user)
            db_sess.commit()
            return redirect('/login')
        return render_template('register.html', title='Регистрация', form=form)
    @app.route('/news/<int:id>', methods=['GET', 'POST'])
    @login_required
    def edit_news(id):
        form = NewsForm()
        if request.method == "GET":
            db_sess = db_session.create_session()
            news = db_sess.query(News).filter(News.id == id,
                                              News.user == current_user
                                              ).first()
            if news:
                form.title.data = news.title
                form.content.data = news.content
                form.is_private.data = news.is_private
            else:
                abort(404)
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            news = db_sess.query(News).filter(News.id == id,
                                              News.user == current_user
                                              ).first()
            if news:
                news.title = form.title.data
                news.content = form.content.data
                news.is_private = form.is_private.data
                db_sess.commit()
                return redirect('/')
            else:
                abort(404)
        return render_template('news.html',
                               title='Редактирование новости',
                               form=form
                               )
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect("/")
    
    @app.route("/back_dep")
    def back_dep():
        return redirect("/departments")
    
    
    @app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
    @login_required
    def news_delete(id):
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            db_sess.delete(news)
            db_sess.commit()
        else:
            abort(404)
        return redirect('/')
    @app.route('/news',  methods=['GET', 'POST'])
    @login_required
    def add_news():
        form = NewsForm()
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            news = News()
            news.title = form.title.data
            news.content = form.content.data
            news.is_private = form.is_private.data
            current_user.news.append(news)
            db_sess.merge(current_user)
            db_sess.commit()
            return redirect('/')
        return render_template('news.html', title='Добавление новости', 
                               form=form)
    @app.route('/departments/add_department',  methods=['GET', 'POST'])
    @login_required
    def add_dep():
        form = DepartmentForm()
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            dep = Department()
            dep.title = form.title.data
            dep.chief = form.chief.data
            dep.members = form.members.data
            dep.email = form.department_email.data
            current_user.dep.append(dep)
            db_sess.merge(current_user)
            db_sess.commit()
            return redirect('/departments')
        return render_template('department.html', title='Добавление отдела', 
                               form=form)
    @app.route('/departments/edit_department/<int:id>', methods=['GET', 'POST'])
    @login_required
    def edit_deps(id):
        form = DepartmentForm()
        if request.method == "GET":
            db_sess = db_session.create_session()
            if current_user.id != 1:
                dep = db_sess.query(Department).filter(Department.id == id,
                                                  Department.user == current_user
                                                  ).first()
            if current_user.id == 1:
                dep = db_sess.query(Department).filter(Department.id == id
                                                  ).first()
            if dep:
                form.title.data = dep.title
                form.chief.data = dep.chief
                form.members.data = dep.members
                form.department_email.data = dep.email
            else:
                abort(404)
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            dep = db_sess.query(Department).filter(Department.id == id,
                                              Department.user == current_user
                                              ).first()
            if current_user.id == 1:
                dep = db_sess.query(Department).filter(Department.id == id
                                                  ).first()
            if dep:
                dep.title = form.title.data
                dep.chief = form.chief.data
                dep.members = form.members.data
                dep.email = form.department_email.data
                db_sess.commit()
                return redirect('/departments')
            else:
                abort(404)
        return render_template('department.html',
                               title='Редактирование работы',
                               form=form
                               )
    @app.route('/departments/delete_department/<int:id>', methods=['GET', 'POST'])
    @login_required
    def deps_delete(id):
        db_sess = db_session.create_session()
        if current_user.id != 1:
            dep = db_sess.query(Department).filter(Department.id == id,
                                              Department.user == current_user
                                              ).first()
        if current_user.id == 1:
            dep = db_sess.query(Department).filter(Department.id == id,
                                              ).first()
        if dep:
            db_sess.delete(dep)
            db_sess.commit()
        else:
            abort(404)
        return redirect('/departments')
    @app.route('/jobs/<int:id>', methods=['GET', 'POST'])
    @login_required
    def edit_jobs(id):
        form = JobsForm()
        if request.method == "GET":
            db_sess = db_session.create_session()
            if current_user.id != 1:
                jobs = db_sess.query(Jobs).filter(Jobs.id == id,
                                                  Jobs.user == current_user
                                                  ).first()
            if current_user.id == 1:
                jobs = db_sess.query(Jobs).filter(Jobs.id == id
                                                  ).first()
            if jobs:
                form.title.data = jobs.job
                form.team_leader.data = jobs.team_leader
                form.work_size.data = jobs.work_size
                form.collaborators.data = jobs.collaborators
                form.is_private.data = jobs.is_finished
            else:
                abort(404)
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            jobs = db_sess.query(Jobs).filter(Jobs.id == id,
                                              Jobs.user == current_user
                                              ).first()
            if current_user.id == 1:
                jobs = db_sess.query(Jobs).filter(Jobs.id == id
                                                  ).first()
            if jobs:
                jobs.job = form.title.data
                jobs.team_leader = form.team_leader.data
                jobs.work_size = form.work_size.data
                jobs.collaborators = form.collaborators.data
                jobs.is_finished = form.is_private.data
                db_sess.commit()
                return redirect('/')
            else:
                abort(404)
        return render_template('jobs.html',
                               title='Редактирование работы',
                               form=form
                               )
    @app.route('/jobs',  methods=['GET', 'POST'])
    @login_required
    def add_jobs():
        form = JobsForm()
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            jobs = Jobs()
            jobs.job = form.title.data
            jobs.team_leader = form.team_leader.data
            jobs.is_private = form.is_private.data
            jobs.work_size = form.work_size.data
            jobs.collaborators = form.collaborators.data
            current_user.jobs.append(jobs)
            db_sess.merge(current_user)
            db_sess.commit()
            return redirect('/')
        return render_template('jobs.html', title='Добавление работы', 
                               form=form)
    @app.route('/jobs_delete/<int:id>', methods=['GET', 'POST'])
    @login_required
    def jobs_delete(id):
        db_sess = db_session.create_session()
        if current_user.id != 1:
            jobs = db_sess.query(Jobs).filter(Jobs.id == id,
                                              Jobs.user == current_user
                                              ).first()
        if current_user.id == 1:
            jobs = db_sess.query(Jobs).filter(Jobs.id == id,
                                              ).first()
        if jobs:
            db_sess.delete(jobs)
            db_sess.commit()
        else:
            abort(404)
        return redirect('/')
    


if __name__ == '__main__':
    main()
    app.run(port=8080, host='127.0.0.1')