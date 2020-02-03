from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, validators, TextField, IntegerField
from wtforms.validators import DataRequired, Length, Required, NumberRange
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_wtf import Form
from wtforms import SelectField

# use this python module for creating python forms and user input 
# import stringfields  so the user can input strings
# use validators in order to prevent the user from inputting details that we don't want e.g correct length of password



class Kinase(FlaskForm):		
	search = StringField('Enter a valid Kinase name', validators=[DataRequired()])
	submit = SubmitField('Search')


class Inhibitor(FlaskForm):		
	search = StringField('Enter a Inhibitor of a Kinase name', validators=[DataRequired()])
	submit = SubmitField('Search')


class FileForm(FlaskForm):
    file = FileField(validators=[FileRequired()])
    submit = SubmitField('Submit')

class Phosphosite(FlaskForm):
	chromosome_number = SelectField('chromosome_number', choices=[('one', '1'),('two', '2'), ('three', '3')])
	karyotypes = SelectField('karyotypes', choices=[('q','c'), ('r','t')])
	submit = SubmitField('Search')

class Parameters(FlaskForm):
	PValue = SelectField('P-Value Threshold: (0.01 or 0.05)', choices=[('0.01', '0.01'),('0.05', '0.05')])
	Fold = SelectField('Fold Change Significance Threshold: (0 - 5)', choices=[('0', '0'),('1', '1'), ('2', '2'),('3', '3'),('4', '4'),('5', '5')])
	Coefficience = IntegerField('Coefficience of Variance Threshold (%)', validators=[DataRequired()])
	submit = SubmitField('Submit')