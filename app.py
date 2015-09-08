import flask
#from flask import Flask
import os
import base64
import json
import requests
import hashlib
import urlparse
from flask import request, Response, session, redirect, send_from_directory
from functools import wraps
from flask import render_template
from werkzeug import secure_filename

# needs secret key defined
from models import initModels, dbSession, getMenusWithPages, Menu, Page, ImageTag

UPLOAD_FOLDER = '/tmp/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

app = flask.Flask(__name__)
app.debug = True
app.secret_key = os.environ['AHA_SECRET_KEY']

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == 'admin' and password == 'secret'

def authenticate():
    """Sends a 401 response that enables basic auth"""

    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def getAdminUsers():
    return os.environ['AHA_ADMIN_EMAILS'].split(',')

def md5(fname):
    hash = hashlib.md5()
    with open(fname) as f:
        for chunk in iter(lambda: f.read(4096), ""):
            hash.update(chunk)
    return hash.hexdigest()

@app.route('/oauth2')
def oauth2():
    url = "https://www.googleapis.com/oauth2/v3/token"
    headers = {
        "X-Api-Version" : "2",
        'content-type' : 'application/x-www-form-urlencoded'
    }
    payload = {
        "code" : request.args['code'],
        "client_id" : os.environ['AHA_GOOGLE_OAUTH2_CLIENT_ID'],
        "client_secret" : os.environ['AHA_GOOGLE_OAUTH2_CLIENT_SECRET'],
        "redirect_uri" : "http://localhost:5000/oauth2",
        "grant_type" : "authorization_code"
    }
    response = requests.post(url, data=payload, headers=headers)
    data = response.json()
    idToken = data['id_token'].split('.')[1]
    if len(idToken) % 4 == 2:
        idToken += "=="
    elif len(idToken) % 4 == 3:
        idToken += "="

    idData = json.loads(base64.b64decode(idToken))
    if idData['email'] in getAdminUsers():
        session['username'] = idData['email']
        return redirect('/admin')

    return 'unrecognized person: %s' % idData['email']

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in session:
            url = 'https://accounts.google.com/o/oauth2/auth?'
            params = {
                "client_id" : os.environ['AHA_GOOGLE_OAUTH2_CLIENT_ID'],
                "response_type" : "code",
                "scope" : "openid email",
                "redirect_uri" : "http://localhost:5000/oauth2",
                "state" : "anti-forgery here"
            }
            url = requests.Request(url=url, params=params).prepare().url
            return redirect(url)

        return f(*args, **kwargs)
    return decorated

@app.route('/')
def home():
    menus = getMenusWithPages()
    return render_template('home.html', menus=menus)

@app.route('/p/<int:pageId>/<dummy>')
def p(pageId, dummy):
    menus = getMenusWithPages()
    page = dbSession.query(Page).get(pageId)
    return render_template('page.html', menus=menus, page=page)

@app.route('/admin')
@requires_auth
def admin():
    return render_template('admin.html')

@app.route('/pages', methods=['GET','POST'])
@requires_auth
def pages():
    if request.method == 'POST': # put page
        title = request.form['title']
        menuId = request.form['menuId']
        page = Page(title=title, menuId=menuId)
        dbSession.add(page)
        dbSession.commit()
        return 'done'
    else:
        return 'done'

@app.route('/pages/<int:pageId>/order', methods=['PATCH'])
@requires_auth
def pageOrder(pageId):
    page = dbSession.query(Page).get(pageId)

    prevOrder = int(request.form['srcIndex'])
    targetOrder = int(request.form['targetIndex'])

    srcMenuId = request.form['srcMenuId']
    targetMenuId = request.form['targetMenuId']

    # remove from one, put in another
    if targetMenuId != srcMenuId:
        page.menuId = targetMenuId
        dbSession.commit()

    reorderMenu(targetMenuId, pageId, targetOrder)

    return 'done'
    
def reorderMenu(menuId, pageId=None, targetOrder=None):
    menu = dbSession.query(Menu).get(menuId)

    pages = dbSession.query(Page).order_by(Page.order).all()

    # make sure the page is in the correct spot
    if pageId:
        index = map(lambda page: page.id, pages).index(pageId)
        if index != targetOrder:
            pages.insert(targetOrder, pages.pop(index))

    for i,page in enumerate(pages):
        page.order = i
    dbSession.commit()

@app.route('/menus', methods=['GET','POST'])
@requires_auth
def menus():
    if request.method == 'POST':
        menu = Menu(title=request.form['title'])
        dbSession.add(menu)
        dbSession.commit()

        return 'done'
    else:        
        menus = getMenusWithPages()

        data = {
            "menus" : menus
        }
        return flask.jsonify(**data)

@app.route('/menus/<int:menuId>', methods=['PATCH'])
@requires_auth
def menu(menuId):
    menu = dbSession.query(Menu).get(menuId)
    menu.title = request.form['title']
    dbSession.commit()

    return 'done'

@app.route('/page/<int:pageId>', methods=['PATCH'])
@requires_auth
def page(pageId):
    page = dbSession.query(Page).get(pageId)
    page.title = request.form['title']
    dbSession.commit()

    return 'done'

@app.route('/layout')
def layout():

    data = {}
    data['widgets'] = [{
        'name' : 'header-template',
        'srcUrl' : _getHeaderUrl()
    }]

    return flask.jsonify(**data)

@app.route('/upload', methods=['POST'])
def upload():
    """Upload a new file."""
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return 'done' #redirect(url_for('uploaded_file',
                      #          filename=filename))

    #if request.method == 'POST':
    #    save(request.files['upload'])
    #    return redirect(url_for('index'))
    #return render_template('upload.html')

def _getHeaderUrl():
    imageTag = dbSession.query(ImageTag).filter(ImageTag.tag == "header").first()
    return '/uploads/' + imageTag.path

@app.route('/header', methods=['GET', 'POST'])
@requires_auth
def header(forcedName=None):
    if request.method == 'POST':
        fileName = secure_filename(urlparse.unquote(request.headers['X-File-Name']))
        if allowed_file(fileName):
            filePath = os.path.join(app.config['UPLOAD_FOLDER'], fileName)
            with open(filePath, 'w') as fd:
                fd.write(request.data)

            # delete existing header
            dbSession.query(ImageTag).filter(ImageTag.tag == "header").delete()

            tag = ImageTag(hash=md5(filePath), tag='header', path=fileName)
            dbSession.add(tag)
            dbSession.commit()

        return 'done'
    else:
        imageTag = dbSession.query(ImageTag).filter(ImageTag.tag == "header").first()
        data = { 'url' : _getHeaderUrl() }

        return flask.jsonify(**data)

# Custom static data
@app.route('/uploads/<path:filename>')
def custom_static(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    initModels()
    app.run(host='0.0.0.0')

