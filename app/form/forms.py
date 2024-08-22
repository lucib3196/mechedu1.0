from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from flask_wtf.file import MultipleFileField, FileRequired,FileField
from wtforms.validators import DataRequired

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
