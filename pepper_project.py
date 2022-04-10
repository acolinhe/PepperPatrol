from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pep.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
db = SQLAlchemy(app)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    img = db.Column(db.Text, unique=True, nullable=False)
    img_name = db.Column(db.Text, nullable=False)
    img_type = db.Column(db.Text, nullable=False)
    caption = db.Column(db.String(200), nullable=False)
    post_date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Post %r>' % self.id


@app.route('/', methods=['GET', 'POST'])
def index():
    posts = Post.query.order_by(desc(Post.post_date)).all()
    return render_template('index.html', tasks=posts)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}


@app.route('/post', methods=['GET', 'POST'])
def post():
    if request.method == 'POST':
        # Parse image
        post_img = request.file['image']
        if not post_img:
            return 'No image uploaded', 400
        filename = secure_filename(post_img.filename)
        if not allowed_file(filename):
            return 'Invalid file uploaded', 400
        post_caption = request.form['caption']
        post = Post(img=post_img.read(), img_name=filename, img_type=post_img.mimetype, caption=post_caption)

        try:
            db.session.add(post)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue creating your post.'
    else:
        return render_template('post.html')


@app.route('/delete/<int:id>')
def delete(id):
    post = Post.query.get_or_404(id)
    try:
        db.session.delete(post)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting this post.'


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    post = Post.query.get_or_404(id)
    if request.method == 'POST':
        post.caption = request.form['caption']
        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was a problem updating this post.'
    else:
        return render_template('update.html', task=post)


if __name__ == '__main__':
    app.run(debug=True)
