from app import app
from app.models import User, Group
from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, BooleanField, SubmitField,
  SelectMultipleField, SelectField, TextAreaField)
from wtforms.validators import (DataRequired, ValidationError, EqualTo, 
  Length)
from flask_wtf.file import FileField, FileAllowed, FileRequired

class LoginForm(FlaskForm) :
  usenm = StringField('Username', validators=[DataRequired(), Length(min=5, max=16)])
  pswrd = PasswordField('Password', validators=[DataRequired(), Length(min=12, max=16)])
  sgnin = SubmitField('Sign In')

class RegistrationForm(FlaskForm) :
  fulnm     = StringField('Fullname', validators=[DataRequired(), Length(min=0, max=80)])
  usenm     = StringField('Username', validators=[DataRequired(), Length(min=5, max=16)]) 
  pswrd     = PasswordField('Password', validators=[DataRequired(), Length(min=12, max=16)])

  # EqualTo is used to compare is the password used when registered is the same both times
  rpt_pswrd = PasswordField('Re-enter Password', validators=[DataRequired(), EqualTo('pswrd'), Length(min=12, max=16)])

  groups    = SelectMultipleField('Request Access to Groups', validators=[DataRequired()], coerce=int)

  rgstr     = SubmitField('Register')
  
  def validate_username(self, username) :
    user = User.query.filter_by(username=usenm.data).first()
    if user is not None :
      raise ValidationError('Username taken. Please enter a new username.')
 
class JumpToGroupForm(FlaskForm) :
  visitgrp = SelectField('Visit a Group', validators=[DataRequired()], coerce=int)
  visit = SubmitField('Visit')

class ConfirmRegistrationForm(FlaskForm) : 
  validusers = SelectMultipleField('Confirm Users', coerce=int)
  confirm    = SubmitField('Confirm')

class AddToGroupForm(FlaskForm) :
  slctgroups = SelectMultipleField('Choose Groups to Join', coerce=int)
  joingrp = SubmitField('Authenticate')

class CreateGroupForm(FlaskForm) : 
  newgroup = StringField('New Group', validators=[Length(min=12, max=16)])
  create   = SubmitField('Create')

class UploadItemForm(FlaskForm) :
  sendtogrp = SelectField('Send an Item to a Group', coerce=int)
  name = StringField('Item Name', validators=[DataRequired(), Length(min=10, max=68)])
  descriptor = TextAreaField('Item Description', validators=[DataRequired(), Length(min=10, max=1000)])
  itemupload = FileField('Choose a File to Import',validators=[FileRequired(),
                                                               FileAllowed(app.config['ALLOWED_EXTENSIONS'], 'Please go to the home page to see the acceptable file extensions.')
                                                              ])
  upload   = SubmitField('Upload')

class ItemInfoForm(FlaskForm) :
  downld = SubmitField('Download')
  delete = SubmitField('Delete')
