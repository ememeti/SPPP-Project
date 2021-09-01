from app import app, db
from app.forms import (LoginForm, RegistrationForm, ConfirmRegistrationForm,
  CreateGroupForm, AddToGroupForm, UploadItemForm, JumpToGroupForm, ItemInfoForm)
from app.models import User, Group, Item, Members
from datetime import datetime, timedelta
from flask import (render_template, Flask, redirect, request, url_for,
  session, flash, send_from_directory)
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
import os
import re


limiter = Limiter(app, key_func=get_remote_address)


@app.route('/')
@app.route('/index')
@limiter.limit('50/minute')
@login_required
def index() :
  # Only logged in users can access this page
  if current_user.is_anonymous :
    flash('Please login to view the page.')
    return redirect(url_for('login'))

  info = [
    {
      'header': 'View Group',
      'body': 'User can pick which groups they want to view. View the logs of past messages sent to specific groups the user is apart of.'
    },
    {
      'header': 'Settings',
      'body': 'Admin can authenticate users, authenticate users joining a group, and creating new names on this page.'
    },
    {
      'header': 'Put',
      'body': 'Users can upload up to 8 MB files to the groups they are apart of.'
    },
    {
      'header': 'Acceptable File Extensions',
      'body': ('jpg, png, img, pdf, \
              gif, doc, docx, ppt, \
              pptx, xls, xlsx, txt, \
              3fr,  ari,  arw,  bay, \
              braw,  crw,  cr2,  cr3, \
              cap,  data,  dcs,  dcr, \
              dng,  drf,  eip,  erf, \
              fff,  gpr,  iiq,  k25, \
              kdc,  mdc,  mef,  mos, \
              mrw,  nef,  nrw,  obm, \
              orf,  pef,  pt,  pxn, \
              r3d,  ra,  raw,  rwl, \
              rw2,  rwz,  sr2,  srf, \
              srw,  tif,  x3f,  webm, \
              mpg,  ogg,  mp4,  mp3, \
              mov,  avi,  wmv,  qt, \
              svd,  ai,  bmp,  tif, \
              c,  cpp,  java,  py, \
              m4v,  odt,  rtf,  tex, wpd')
    },
    {
      'header': 'View Item Information',
      'body': 'Go to specific group pages and click on the hyperlink that highlights the item name to go to a separate page that shows details about the item.' 
    },
    {
      'header': 'View User Information',
      'body': 'Go to specific pages and click on the hyperlink that highlights the username of the individual who posted the item to go to a separate page that shows details about the groups they\'re in and the items they posted in each group.' 
    }
  ]

  return render_template('index.html', title='Home', info=info)


@app.route('/login', methods=['GET','POST'])
@limiter.limit('10/minute')
def login() :
  if current_user.is_authenticated :
    return redirect(url_for('index'))
  form = LoginForm()
  if form.validate_on_submit() :
    user = User.query.filter_by(username=form.usenm.data).first()

    # Catches if there was no username that was matched in the database
    #   or if the password doesn't match the register user
    if user is None or not user.check_pswrd(form.pswrd.data) :
      flash('Invalid username or password.')
      return redirect(url_for('login'))

    # Prevents users who haven't been authenticated from
    #   logging in.
    if user.authen == False :
      flash('The admin has not confirmed you, yet.')
      return redirect(url_for('login'))

    login_user(user, remember=False)
    next_page = request.args.get('next')
    if not next_page or url_parse(next_page).netloc != '' :
      next_page = url_for('index')
    return redirect(next_page)
  return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
  logout_user()
  return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
@limiter.limit('15/hour')
def register() :
  # Catches if the user is already logged in
  # Redirects back to the main page
  if current_user.is_authenticated :
    return redirect(url_for('index'))

  # Stores Group objects for every group name
  allgroups = Group.query.all()

  # When database is initialized, we need to have
  #   a default group that admin and new users 
  #   can join
  if not allgroups :
    group = Group(name='Main')

    db.session.add(group)
    db.session.commit()

    return redirect(url_for('register'))

  form = RegistrationForm()

  form.groups.choices = [(groupnm.id, groupnm.name) for groupnm in allgroups]

  # Catches when the user presses the submit button
  if form.validate_on_submit():
    user = User(fullname=form.fulnm.data, username=form.usenm.data)

    regex_pass = re.compile('^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[-+_!@#$%^&*., ?]).+$')
    
    # Check if a password has at least one uppercase, one lowercase, and special character
    #   and at least one digit in it
    if re.search(regex_pass, form.pswrd.data) :
      user.set_pswrd(form.pswrd.data)
    else :
      flash('Passwords need at least one capitalized letter, one lowercase letter, a digit, and a special character')
      return redirect(url_for('register'))

    # When registering admin, they will be able to bypass
    #   the authentication since they're the admin
    if form.usenm.data == 'admin' :
      user.set_authen( True )
      user.set_groupauthen( True )
    else :
      user.set_authen( False )
      user.set_groupauthen( False )
      flash('Please wait for the admin to confirm your registration.')

    if form.usenm.data == 'admin' :      
      # Add admin as a member of the Main group
      joinMain = Members(username=user.username, groupname='Main')

      # Add the admin to the database
      db.session.add(user)

      # Adds user to group Main
      db.session.add(joinMain)

      # Write the admin to our database without needing to join a group
      db.session.commit() 

      return redirect(url_for('login'))

    # A set of ids are returned, so we'll match
    #   those ids with the ones in the database
    for i in form.groups.data :
      # Finds the Group with the same id
      group = Group.query.filter_by(id=i).first()

      rqstGroups = Members(username=user.username, groupname=group.name)

      # Add the groups the user wants to join
      db.session.add(rqstGroups)
 
    # Add the user to the database
    db.session.add(user)

    # We do this one more time to commit the new table
    db.session.commit() 

    # User will have to sign in once they've been 
    #   authenticated by the admin
    return redirect(url_for('login'))
  return render_template('register.html', title='Register', form=form)


@app.route('/jump', methods=['GET', 'POST'])
@login_required
@limiter.limit('200/hour')
def jump():
  # Only people who have been authenticated to join groups can post items
  if(current_user.joingroups is False) :
    flash('The admin has not authenticated you being in a group.')
    return redirect(url_for('index'))

  form = JumpToGroupForm()

  # Stores the Group(s) that the User is apart of
  # allgroups = Group.query.all()
  allgroups = Members.query.filter_by(username=current_user.username).all()

  #form.visitgrp.choices = [(group.id, group.name) for group in allgroups]
  form.visitgrp.choices = [(group.id, group.groupname) for group in allgroups]

  if form.validate_on_submit() :
    chosen = Members.query.filter_by(id=form.visitgrp.data).first()
    join = Group.query.filter_by(name=chosen.groupname).first()

    return redirect(url_for('group', groupname=join.name))

  return render_template('jump.html', title='View Messages in a Group', form=form)


@app.route('/group/<groupname>', methods=['GET', 'POST'])
@login_required
@limiter.limit('200/hour')
def group(groupname):
  # Only logged in users can access this page
  if current_user.is_anonymous :
    flash('Please login to view the page.')
    return redirect(url_for('login'))
 
  # Prevents users who haven't been authenticated from
  #   logging in.
  if current_user.authen == False :
    flash('The admin has not confirmed you, yet.')
    return redirect(url_for('login'))

  # Only people who have been authenticated to join groups can view groups
  if current_user.joingroups is False :
    flash('The admin has not authenticated you being in a group.')
    return redirect(url_for('index'))

  # If the user inputs a <groupname> in the URL and that group
  #   doesn't exist, then we go into a 404 page
  group = Group.query.filter_by(name=groupname).first_or_404()

  member = Members.query.filter_by(username=current_user.username, groupname=group.name).first() 
  
  # Only people who are members of the groups can view the group
  if(current_user.joingroups is True and member is None) :
    flash('You are not a member of this group.')
    return redirect(url_for('index'))

  items = Item.query.filter_by(group_name=group.name).order_by(Item.creation.desc())

  return render_template('group.html', group=group, items=items)


@app.route('/item/<itemname>', methods=['GET', 'POST'])
@login_required
@limiter.limit('5/minute')
def item(itemname):
  # Only logged in users can access this page
  if current_user.is_anonymous :
    flash('Please login to view the page.')
    return redirect(url_for('login'))
 
  # Prevents users who haven't been authenticated from
  #   logging in.
  if current_user.authen == False :
    flash('The admin has not confirmed you, yet.')
    return redirect(url_for('login'))

  # Only people who have been authenticated to join groups can view groups
  if current_user.joingroups is False :
    flash('The admin has not authenticated you being in a group.')
    return redirect(url_for('index'))

  iteminfo = Item.query.filter_by(name=itemname).first_or_404()

  form = ItemInfoForm()

  # Catches when a user wants to download a file
  if form.downld.data and form.validate() :
    iteminfo.lastaccess = datetime.utcnow()
    db.session.commit()
    flash('File successfully downloaded.')
    return send_from_directory(app.instance_path+'/instance/items',
                        str(iteminfo.id) + '_'+ iteminfo.fname, 
                        as_attachment=True)
 
  # Catches when we want to delete a record
  if form.delete.data and form.validate() :
    # Deleting an item is reserved for the original poster
    #   and/or the Admin
    if current_user.username != iteminfo.author_user and current_user.username != 'admin' :
      flash('Only the original poster or Admin can delete Items.')
      return redirect(url_for('item', itemname=iteminfo.name))
    else :
      if os.path.isfile(app.instance_path + '/instance/items/' + str(iteminfo.id) + '_' + iteminfo.fname) :
        os.remove(app.instance_path + '/instance/items/' + str(iteminfo.id) + '_' + iteminfo.fname)
        Item.query.filter_by(id=iteminfo.id).delete()
        # Make sure to write the changes to the database
        db.session.commit()
        flash('Item successfully deleted.')
        return redirect(url_for('jump'))

  return render_template('item.html', title='Item Information', form=form, item=iteminfo)


@app.route('/view/<viewname>')
@login_required
@limiter.limit('50/hour')
def view(viewname) :
  # Prevents users who haven't been authenticated from
  #   logging in.
  if current_user.authen == False :
    flash('The admin has not confirmed you, yet.')
    return redirect(url_for('login'))

  user = User.query.filter_by(username=viewname).first_or_404()

  # Prevents users who haven't been authenticated from
  #   viewing their page.
  if user.authen == False :
    flash('This user has not been authenticated, yet.')
    return redirect(url_for('index'))
  
  groups = Members.query.filter_by(username=user.username).all()

  #groups = Group.query.filter_by(name=member.groupname).all()

  allitems = Item.query.filter_by(author_user=viewname).order_by(Item.creation.desc())
  
  return render_template('view.html', title='View User Information', user=user, groups=groups, items=allitems)


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings() :
  if current_user.username != 'admin' :
    flash('Only accessible by admin')
    return redirect(url_for('index'))

  # Stores User objects that are awaiting to be authenticated
  newusers = User.query.filter_by(authen=(False)).all()

  # Stores User objects who haven't joined groups and have 
  #   been authenticated by the admin
  usergroups = User.query.filter_by(authen=(True), joingroups=(False)).all()

  regisform = ConfirmRegistrationForm() 
  groupform = AddToGroupForm() 
  createform = CreateGroupForm()

  regisform.validusers.choices = [(newuser.id, newuser.username) for newuser in newusers]

  # Catches when admin wants to authenticate users
  if regisform.confirm.data and regisform.validate() :
    # A set of ids are returned, so we'll match
    #   those ids with the ones in the database
    for i in regisform.validusers.data :
      # Stores the user object with the matching id
      user = User.query.filter_by(id=i).first()

      # Represents the admin authenticating the user
      user.set_authen( True )

      # Writes the changes to the database
      db.session.commit()
    return render_template('settings.html', title='Settings', regisform=regisform, 
      groupform=groupform, createform=createform)

  groupform.slctgroups.choices = [(usergroup.id, usergroup.username) for usergroup in usergroups]

  # Catches when admin wants to authenticate users
  if groupform.joingrp.data and groupform.validate() :
    # A set of ids are returned, so we'll match
    #   those ids with the ones in the database
    for i in groupform.slctgroups.data :
      # Stores the user object with the matching id
      user = User.query.filter_by(id=i).first()

      # Represents the admin authenticating the user
      user.set_groupauthen( True )

      # Writes the changes to the database
      db.session.commit()
    return render_template('settings.html', title='Settings', regisform=regisform, 
      groupform=groupform, createform=createform)
  
  # Catches when admin wants to create a new group
  if createform.create.data and createform.validate() :
    # Creates a group object
    addgroup = Group(name=createform.newgroup.data)

    member = Members(username=current_user.username, groupname=addgroup.name)

    # Add the group to the database
    db.session.add(addgroup)

    # Add the group to the database
    db.session.add(member)

    # Write the group to the database
    db.session.commit()

    return render_template('settings.html', title='Settings', regisform=regisform, 
      groupform=groupform, createform=createform)
 
  return render_template('settings.html', title='Settings', regisform=regisform, 
    groupform=groupform, createform=createform)

@app.route('/put', methods=['GET', 'POST'])
@login_required
@limiter.limit('10/hour')
def put() :
  # Only people who have been authenticated to join groups can post items
  if(current_user.joingroups is False) :
    flash('You cannot post items in groups until the Admin authenticates you.')
    return redirect(url_for('index'))
 
  # Prevents users who haven't been authenticated from
  #   logging in.
  if current_user.authen == False :
    flash('The admin has not confirmed you, yet.')
    return redirect(url_for('login'))

  # Only logged in users can access this page
  if current_user.is_anonymous :
    flash('Please login to view the page.')
    return redirect(url_for('login'))

  form = UploadItemForm()
 
  # Stores the Group(s) that the User is apart of
  #joinedgroups = Group.query.all()
  joinedgroups = Members.query.filter_by(username=current_user.username).all()

  form.sendtogrp.choices = [(group.id, group.groupname) for group in joinedgroups]

  if form.validate_on_submit() :
    # Stores the file object in order to validate that it's a safe file
    f = form.itemupload.data

    # Before we store the filename into our database,
    #   we need to make sure the data isn't forged
    #   and the filename isn't dangerous
    # So a name like ../../../../home/username/.bashrc
    #   will be turned into bashrc
    filename = secure_filename(f.filename)

    # Cut any filename longer than 68 characters
    if len(filename) > 68 :
      filename = filename[-68:]

    chosen = Members.query.filter_by(id=form.sendtogrp.data).first()

    # Finds the Group object that matches the one that the user selected
    group = Group.query.filter_by(name=chosen.groupname).first()

    item = Item(name=form.name.data, fname=filename,
      metatype=f.content_type,
      metasize=f.content_length,
      author_user=current_user.username,
      descriptor=form.descriptor.data,
      creation=datetime.utcnow(),
      lastaccess=datetime.utcnow(),
      group_name=group.name)

    db.session.add(item)

    db.session.commit()

    # Saves the file on a directory that can later be used
    #   to save the image to another user's system
    f.save(os.path.join(app.instance_path, 'instance/items', str(item.id) + '_'+ filename ))

    flash('Item successfully uploaded.')

    return redirect(url_for('put'))
    
  return render_template('put.html', title='Put', form=form)

# User is automaticaly logged out after 2 minute of idle time
@app.before_request
def before_request():
  session.permanent = True
  app.permanent_session_lifetime = timedelta(minutes=2)

if __name__ == "__main__":
  app.run(debug=True)
