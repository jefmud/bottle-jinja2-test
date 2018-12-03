# An example of a simple Bottle App
import jinja2
#import bcrypt
from bottle import (TEMPLATE_PATH, redirect, request, response,
                      route, run, template, jinja2_view)
                      
from peewee import *

TEMPLATE_PATH[:] = ['templates']


DB = SqliteDatabase(":memory:")
secret_key = '<kOPIU8*(6N#JWT^La'

class User(Model):
  username = CharField(unique=True)
  displayname = CharField(default="")
  password = CharField()
  is_admin = BooleanField(default=False)
  
  def authenticate(self, password):
    if password == self.password:
      return True
    else:
      return False
  
  class Meta:
    database = DB

def connect():
  try:
    DB.connect()
  except:
    pass
  
def get_user_by_username(username):
  """return a user object with a particular username"""
  connect()
  user = User.select().where(User.username==username)
  if len(user):
    return user[0]
  
  return None
  
  
@route('/')
@jinja2_view('index.html')
def index():
  """slightly complex template under Jinja2 and Materialize"""
  if request.get_cookie('is_authenticated', secret=secret_key):
    username = request.get_cookie('username', secret=secret_key)
    user = get_user_by_username(username)
    displayname = "Stranger"
    if user:
      if user.displayname:
        displayname = user.displayname
      else:
        displayname = user.username
  else:
    displayname = ""
  context = {
    'title': 'Repl.it test for Bottle',
    'name': displayname,
  }
  return context

@route('/register')
@jinja2_view('register.html')
def register():
  """show user registration"""
  context = {}
  return context
  
@route('/register', method='POST')
def register_post():
  """handle user registration"""
  errors = []
  username = request.forms.get('username')
  displayname = request.forms.get('displayname')
  password = request.forms.get('password')
  confirm = request.forms.get('confirm')
  
  if password != confirm:
    errors.append("Passwords did not match!")
  
  if get_user_by_username(username):
    errors.append("Username already exists!")
  
  if errors == []:
    connect()
    User.create(username=username, password=password)
    return 'Thanks for registering! <a href="/login">Proceed to login</a>'
  
  errors = "<br />\n".join(errors)
  return '<p style="font-color:red;">{}</p><p><a href="/register">Try Again.</a></p>'.format(errors)

@route('/users')
def users():
  connect()
  users = User.select()
  html = ['<ol>']
  for user in users:
    html.append('<li>username={} displayname={}</li>'.format(user.username, user.displayname))
  html.append('</ol>')
  return "\n".join(html)
    

@route('/login')
@jinja2_view('login.html')
def login():
  """A user login"""
  context = {}
  return context

@route('/login', method='POST')
def login_post():
    username = request.forms.get('username')
    password = request.forms.get('password')
    connect()
    user = User.select().where(User.username==username)
    if len(user):
      if user[0].authenticate(password):
        response.set_cookie("username", username, secret=secret_key)
        response.set_cookie("is_authenticated", True, secret=secret_key)
        return redirect("/")
        
    return "<p>Login failed. <a href='/login'>Try again.</a></p>"
  
@route('/logout')
def logout():
  """A user logs out"""
  response.set_cookie("username", "", secret=secret_key)
  response.set_cookie("is_authenticated", False, secret=secret_key)
  return """You are now logged out. Thank you for spending some quality time with us!<br>
  <a href="http://repl.it">Return to Repl.it Community</a>
  """
  
@route('/hello/<name>')
def index(name):
  """simple example of template"""
  return template('<b>Hello {{name}}</b>!', name=name)

@route('/starter')
@jinja2_view('starter-theme.html')
def starter_theme():
  context = {}
  return context
  
def init_database():
  connect()
  DB.create_tables([User])
  try:
    User.create(username="admin", password="adminme", is_admin=True)
    User.create(username="user", password="password")
    User.create(username='barney', password='secret', displayname='Barney The Dinosaur')
  except:
    pass
  
init_database()
run(host='0.0.0.0', port=8080)
