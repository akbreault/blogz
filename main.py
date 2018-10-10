# TODO: display indiv entries per assignment


from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:buildablog@localhost:8889/build-a-blog'
db = SQLAlchemy(app)
app.secret_key = 'z448lHdz&aQ4C'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))

    def __init__(self, title, body):
        self.title = title
        self.body = body 



@app.route('/blog')
def index():
    
    if len(request.args) == 0:  
        blogs = Blog.query.all()
        return render_template('blog.html', blogs=blogs)
    
    else:
       id = request.args.get('id', '')
       blog = Blog.query.get(id)
       title = blog.title
       body = blog.body

       return render_template('blogpost.html', title=title, body=body)


@app.route('/new-post', methods=['GET','POST'])
def add_post():

    title_error = ''
    body_error = ''
    
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
    
        if len(title) == 0:
            title_error = 'Please fill in the title'
        
        if len(body) == 0:
            body_error = 'Please fill in the body'

        if not title_error and not body_error:
            new_blog = Blog(title, body)
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/blog?id={0}'.format(new_blog.id))
        else:
            return render_template('newpost.html', title=title, title_error=title_error, body=body, body_error=body_error)
    
    return render_template('newpost.html')


if __name__ == '__main__':
    app.run()