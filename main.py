from flask import Flask, render_template, flash, redirect, url_for, abort
from flask_login import UserMixin, current_user, LoginManager, login_user
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap5
from forms import SubscribeForm
from emails import Emails
from datetime import datetime
import sqlalchemy.exc
from functools import wraps
import os

weather_app = Flask(__name__)
weather_app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
Bootstrap5(weather_app)

weather_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy()
db.init_app(weather_app)

login_manager = LoginManager()
login_manager.init_app(weather_app)


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


def admin_only(f):
    # Only lets the admin send mail through the 'sendmail' route
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function


class User(UserMixin, db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    email = db.Column(db.String(100))
    location = db.Column(db.String(100))


with weather_app.app_context():
    db.create_all()


@weather_app.route('/', methods=['GET', 'POST'])
def subscribe():
    form = SubscribeForm()
    if form.validate_on_submit():
        try:
            new_user = User(
                username=form.username.data,
                email=form.email.data,
                location=form.location.data
            )
            result = db.session.execute(db.select(User).where(User.email == form.email.data))
            user = result.scalar()

            if not user:
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user)
                return redirect(url_for('success'))
            else:
                flash("Subscriber already exists!")

        except sqlalchemy.exc.IntegrityError:
            flash("Subscriber already exists!")

    return render_template('index.html', form=form)


@weather_app.route('/success')
def success():
    # Confirms users subscription
    return render_template('success.html')


@admin_only
@weather_app.route('/sendmail')
def sendmail():
    emails = Emails()
    all_cities = []
    all_emails = []
    once_a_day = True

    # Checks time before emailing
    now = datetime.now()

    while once_a_day:
        if 5 < now.hour < 7:
            # Retrieves data from the database
            all_cities = [(row.User, row.location)[0:8:1][1] for row in db.session.query(User, User.location).all()]
            all_emails = [(row.User, row.email)[0:8:1][1] for row in db.session.query(User, User.email).all()]
            # Requests location co-ordinates using user location.
            for i in range(len(all_emails)):
                emails.send_emails(email=all_emails[i], params=emails.get_geocodes(city=all_cities[i - 1]))
            return redirect(url_for('subscribe'))
        once_a_day = False

    if now.hour == 4:
        once_a_day = True
    return render_template('sendmail.html')


if __name__ == '__main__':
    weather_app.run(debug=True, port=5007)

