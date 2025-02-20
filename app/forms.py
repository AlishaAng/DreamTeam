
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, validators, TextField,IntegerField, DecimalField
from wtforms.validators import DataRequired, Length, EqualTo, Required, NumberRange
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
	chromosome = SelectField('Chromosome number', choices= [],  validators=[DataRequired()])
	karyotype = SelectField('Karyotypes', choices=[], validators=[DataRequired()])
	submit = SubmitField('Submit')


class Substrate(FlaskForm):
	search = StringField('Enter a valid Substrate name', validators=[DataRequired()])
	submit_substrate = SubmitField('Search')


class Parameters(FlaskForm):
    PValue = DecimalField('P-Value Threshold: (0.01 - 0.05)', validators=[DataRequired(), NumberRange(min=0, max=0.05)])
    Coefficience = DecimalField('Coefficient of Variance Threshold: (0 - 3)', validators=[DataRequired(), NumberRange(min=0,max=3)])
    Fold = SelectField('Fold Change Significance Threshold: (0 - 5)', choices=[('0', '0'),('1', '1'), ('2', '2'),('3', '3'),('4', '4'),('5', '5')])
    Sub = SelectField('Minimum Number of Substrates for Enrichment Visualisation: (0 - 5)', choices =[('0', '0'),('1', '1'), ('2', '2'),('3', '3'),('4', '4'),('5', '5')])
    submit = SubmitField('Submit')
