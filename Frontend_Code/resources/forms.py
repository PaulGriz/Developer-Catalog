from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class NewCategory(FlaskForm):
    name = StringField('name', validators=[DataRequired("Enter New Category Name")])
    submit = SubmitField("Submit")