

from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
db = SQLAlchemy(app)
app.secret_key = 'z448lHdz&aQ4C'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(10000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password




@app.before_request
def require_login():
    allowed_routes = ['login', 'list_blogs', 'index' , 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')



@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users, page_title="Homepage")



@app.route('/blog')
def list_blogs():
    if len(request.args) == 0:  
        blogs = Blog.query.all()
        
    
        if len(blogs) > 0:
            return render_template('blog.html', blogs=blogs, page_title="Blog Posts")

        else: 
            return render_template('blog.html', page_title="Blog Posts")
    

    elif request.args.get('id') != None:
       id = request.args.get('id', '')
       blog = Blog.query.get(id)
       title = blog.title
       body = blog.body

       id = blog.owner_id
       user = User.query.get(id)
       username = user.username


       return render_template('blogpost.html', title=title, body=body, username=username, user=user, page_title="Blog Post")


    elif request.args.get('user') != None:
        id = request.args.get('user', '')
        user = User.query.get(id)
        
        blogs = user.blogs

        
        return render_template('singleUser.html', user=user, blogs=blogs, page_title="This User's Posts")



@app.route('/signup', methods=['POST', 'GET'])
def signup():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        username_error = ''
        password_error = ''
        verify_error = ''
        unique_error = ''

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            unique_error = 'Sorry! that username is taken'

        if len(password) < 3:
            password_error = 'Unfortunately your password is too short - it must be more than 3 characters'
        
        if len(username) < 3:
            username_error = 'Unfortunately your username is too short - it must be more than 3 characters'
        
        if password != verify:
            verify_error = "Your passwords don't match"


        if not existing_user and (len(username_error)==0) and (len(password_error)==0) and (len(verify_error)==0):
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/new-post')
        else:
            return render_template('signup.html', username=username, username_error=username_error, password_error=password_error, verify_error=verify_error, unique_error=unique_error, page_title="Signup Error")

    return render_template('signup.html', page_title='Signup')



@app.route('/login', methods=['POST', 'GET'])
def login():

    username_error = ''
    password_error = ''

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session['username'] = username
            return redirect('/new-post')

        elif user and user.password != password:
            password_error = 'Password does not match established password for this username'
        
        else:
            username_error = 'No such username'
        
        return render_template('login.html', username=username, username_error=username_error, password_error=password_error, page_title="Log In Error")

    return render_template('login.html', page_title="Log In")



@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')



@app.route('/new-post', methods=['GET','POST'])
def add_post():

    title_error = ''
    body_error = ''

    owner = User.query.filter_by(username=session['username']).first()
    
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
    
        if len(title) == 0:
            title_error = 'Please fill in the title'
        
        if len(body) == 0:
            body_error = 'Please fill in the body'

        if not title_error and not body_error:
            new_blog = Blog(title, body, owner)
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/blog?id={0}'.format(new_blog.id))
        else:
            return render_template('newpost.html', title=title, title_error=title_error, body=body, body_error=body_error, page_title="Posting Error")
    
    return render_template('newpost.html', page_title="New Post")



if __name__ == '__main__':
    app.run()