from flask.app import Flask
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, BooleanField,TextAreaField
from flask_wtf.file import MultipleFileField, FileRequired,FileField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from ..db_models.models import User
from wtforms import ValidationError

class QuestionForm(FlaskForm):
    """
    A FlaskForm for generating a question using a string input.

    This form is used to input a question string, which will be processed to generate
    content based on the user's input. It includes a text field for entering the question 
    and a submit button to initiate the generation process.

    Attributes:
        question (StringField): A text field where the user can input the question they want to generate.
        submit (SubmitField): A button to submit the form and trigger the generation process.

    Args:
        FlaskForm (FlaskForm): Inherits from FlaskForm, which provides the base functionality for forms in Flask.
    """
    question = StringField("Enter question to generate", validators=[DataRequired()])
    module_name = StringField("Enter Name of Module",validators=[DataRequired()])
    submit = SubmitField('Generate')


class ImageForm(FlaskForm):
    """
    A FlaskForm for uploading multiple image files and submitting them for processing.

    This form allows users to upload one or more image files, which can then be processed
    based on the user's needs. It includes a file upload field for selecting multiple files
    and a submit button to initiate the file processing.

    Attributes:
        files (MultipleFileField): A file upload field that allows the user to select and upload multiple files. 
                                   The field is validated to ensure that at least one file is selected.
        submit (SubmitField): A button to submit the form and trigger the processing of the uploaded files.

    Args:
        FlaskForm (FlaskForm): Inherits from FlaskForm, which provides the base functionality for forms in Flask.
    """
    files = MultipleFileField(validators=[FileRequired()])
    submit = SubmitField('Generate')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField("Password",validators = [DataRequired()])
    remember_me = BooleanField("Keep Me Logged In")
    submit = SubmitField("Log In")

class SignUp(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired(), Length(1, 64)])
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField("Sign Up")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')
        
class UPDATE_CODE(FlaskForm):
    code = TextAreaField('Code', validators=[DataRequired()])
    save = SubmitField("Save Code")
