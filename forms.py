from flask_wtf import FlaskForm
from wtforms import StringField, SearchField, EmailField, SubmitField
from wtforms.validators import DataRequired


class SubscribeForm(FlaskForm):
    username = StringField('Name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    location = SearchField('Where do you live? (Ex. Mumbai)', validators=[DataRequired()])
    save = SubmitField('save')

