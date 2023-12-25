from inspect import getcomments, getfile
from plistlib import UID
from flask import Flask, redirect, render_template, request, url_for, session, flash, make_response #belum ada flash di htmlnya
from random import *
from functools import wraps
from model import Model as mdl
from flask_uploads import UploadSet, configure_uploads, IMAGES
import jwt
import datetime as dt
from werkzeug.datastructures import FileStorage
from clarifai_grpc.grpc.api import service_pb2
from clarifai_grpc.grpc.api.resources_pb2 import Input, Image, Data
from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api.status import status_code_pb2
from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc
import os
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
from validate_email_address import validate_email
import random

##################################################################################################
# In this section, we set the user authentication, user and app ID, model details, and the URL
# of the image we want as an input. Change these strings to run your own example.
#################################################################################################

# Your PAT (Personal Access Token) can be found in the portal under Authentification
PAT = 'e6ce90703bd74b2ba659181a2fc4b69a'
# Specify the correct user_id/app_id pairings
# Since you're making inferences outside your app's scope
USER_ID = 'clarifai'
APP_ID = 'main'
# Change these to whatever model and image URL you want to use
MODEL_ID = 'moderation-recognition'
MODEL_VERSION_ID = 'aa8be956dbaa4b7a858826a84253cab9'
IMAGE_URL = 'https://samples.clarifai.com/metro-north.jpg'

##################################################################################################
# In this section, we set the user authentication, user and app ID, model details, and the URL
# of the image we want as an input. Change these strings to run your own example.
#################################################################################################

app = Flask(__name__)
app.config["SECRET_KEY"] = "123"

app.config['UPLOADED_PHOTOS_DEST'] = 'static/img'
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)

kolours = ["rgb(25, 62, 68, 0.95)", "rgb(99, 56, 117, 0.95)",
    "rgb(0, 130, 97, 0.95)", "rgb(200, 109, 75, 0.95)", "rgb(38, 59, 167, 0.95)",
    "rgb(118, 40, 40, 0.95)", "rgb(80, 32, 123, 0.95)", "rgb(77, 84, 154, 0.95)",
    "rgb(183, 92, 103, 0.95)", "rgb(18, 149, 166, 0.95)"]

# Configure Flask-Mail settings
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'allanbilfaqih214@gmail.com'  # Replace with your Gmail address
app.config['MAIL_PASSWORD'] = 'pucq qesv pacg nary'  # Replace with your Gmail password
app.config['MAIL_DEFAULT_SENDER'] = 'allanbilfaqih214@gmail.com'  # Replace with your Gmail address


mail = Mail(app)

# A dictionary to store verification codes for email addresses
email_verification_codes = {}

# fungsi jwt dan session
def clear_session_on_startup():
    session.clear()

def require_api_token(func):
    @wraps(func)
    def check_token(*args, **kwargs):
        if 'api_session_token' not in session:
            return redirect(url_for("newest"))

        try:
            data = jwt.decode(session["api_session_token"], app.config["SECRET_KEY"])
        except jwt.ExpiredSignatureError:
            # Token has expired
            session.clear()
            session["msg_color"] = "warning"
            flash("Token Expired. Please log in again.")
            return redirect(url_for("index"))  # Change "newest" to the appropriate route ('/') in your application
        except jwt.InvalidTokenError:
            session.clear()
            session["msg_color"] = "danger"
            flash("Invalid Token. Please log in again.")
            return redirect(url_for("newest"))

        return func(*args, **kwargs)

    return check_token

#############################################################################################################
#PEEKYPUP PAGES
#############################################################################################################

#logout
@app.route('/logout')
def logout():
    session.clear()
    session["uid"] = None
    session["msg_color"] = "warning"
    flash("Logged Out!")
    return redirect(url_for("newest"))

#register
@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/registering", methods=["POST"])
def registering():
    newMdl = mdl
    uname = request.form["username"]
    email = request.form["email"]
    pwd = request.form["password"]
    repwd = request.form["repassword"]

    if not validate_email(email):
        session["msg_color"] = "warning"
        flash("Invalid email address.")
        return redirect(url_for("register"))

    # Generate a random verification code
    verification_code = str(random.randint(1000, 9999))

    # Store the verification code for this email
    email_verification_codes[email] = verification_code

    session["registration_username"] = uname
    session["registration_password"] = pwd

    # Send the verification code to the user
    send_verification_email(email, verification_code)

    # Add a message to inform the user
    session["msg_color"] = "info"
    flash("A verification code has been sent to your email. Please check your inbox.")

    # Redirect the user to a verification page where they can enter the code
    return redirect(url_for("verify_email", email=email))

def send_verification_email(email, verification_code):
    subject = "Email Verification Code"
    body = f"Your verification code is: {verification_code}"

    message = Message(subject=subject, recipients=[email], body=body)

    try:
        mail.send(message)
    except Exception as e:
        # Handle email sending failure, e.g., log the error
        print(f"Error sending email: {e}")
        # You might want to redirect the user to a page informing them to try again
        session["msg_color"] = "danger"
        flash("Error sending verification code. Please try again.")
        return redirect(url_for("register"))

@app.route("/verify_email/<email>", methods=["GET", "POST"])
def verify_email(email):
    if request.method == "POST":
        # User submitted the verification code
        user_code = request.form["verification_code"]
        stored_code = email_verification_codes.get(email)

        # Retrieve values from the session
        uname = session.get("registration_username")
        pwd_from_session = session.get("registration_password")

        if user_code == stored_code:
            # Verification successful, proceed with registration
            newMdl = mdl

            # Your registration logic here...
            if(newMdl.registering(uname, pwd_from_session, dt.datetime.now(), 0, email)):
                session["msg_color"] = "success"
                flash("Sign Up Success!")
                return redirect(url_for("login"))
            else:
                session["msg_color"] = "danger"
                flash("Something's Wrong! Sorry fo the inconveniences.")
                return redirect(url_for("register"))
        else:
            # Incorrect verification code
            session["msg_color"] = "danger"
            flash("Incorrect verification code. Please try again.")
            return redirect(url_for("verify_email", email=email))

    # Render the verification code input form
    return render_template("verify_email.html", email=email)

# login page route
@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/loggin_in", methods=["POST"])
def loggin_in():
    clear_session_on_startup()
    newMdl = mdl()
    username = request.form["username"]
    password = request.form["password"]
    if(username and password):
        # variable row akan diisi dengan hasil return dari fungsi get_user_data yang berada di model.p
        row = newMdl.loggin_in(username)
        # cek jika row empty
        if (row is not None):
            # jika password dan row[4] (row index ke 4) isinya sama maka
            if(row[2] == password):
                # variable token akan terisi dengan hasil encode-an dari jwt
                token = jwt.encode({
                    "user": username,
                    "exp": dt.datetime.utcnow() + dt.timedelta(minutes=15)
                },
                app.config["SECRET_KEY"])
                # lalu data data tersebut akan dimasukkan ke delam session
                session["api_session_token"] = token.decode("utf-8")
                session["uid"] = row[0]
                session["uname"] = row[1]
                session["pwd"] = row[2]
                session["regtime"] = row[3]
                session["isadmin"] = row[4]
                session["msg_color"] = "success"
                flash("Logged In!")
                return redirect(url_for("auth"))
            else:
                session["msg_color"] = "warning"
                flash("Incorrect Username or Password")
                return redirect(url_for("login"))

        else:
            session["msg_color"] = "danger"
            flash("Incorrect Username or Password")
            return redirect(url_for("login"))

# auth route
@app.route("/auth")
@require_api_token
def auth():
    return redirect(url_for("newest"))

# update view count (adding new entry)
@app.route('/add_viewcounts', methods=['POST']) #note mungkin tambah delay/limit view biar gk kena abuse. (maybe session?)
def increment_view_count():
    try:
        data = request.get_json()
        image_ids = data.get('imageIds', [])

        if not image_ids:
            return make_response('No image IDs provided', 400)

        # Assuming add_viewcounts supports batch inserts
        newMdl = mdl
        newMdl.add_viewcounts(image_ids, dt.datetime.now())

        return make_response('Success', 200)

    except Exception as e:
        print(f"Error adding view counts: {str(e)}")
        return make_response('Internal Server Error', 500)


# < home route
@app.route("/")
def index():
    session["msg_color"] = "secondary"
    return redirect(url_for("newest"))

@app.route("/home/newest")
def newest():
    newMdl = mdl
    randLine = newMdl.funnyLine()
    randBG = randint(1,9)
    getImageTags = newMdl.get_imagetags()
    getImagesNew = newMdl.get_images_newest(session.get("uid")) if session and "uid" in session else newMdl.get_images_newest(None)
    getTags = newMdl.get_tags()
    getTotal = newMdl.count_images()

    return render_template("index.html",
    line = randLine, bg = randBG, newImg = getImagesNew, slect = "Newest", msg_color = session["msg_color"],
    imgtgs = getImageTags, kolor = kolours, tags = getTags, total = getTotal)

@app.route("/home/random")
def randomz():
    newMdl = mdl
    randLine = newMdl.funnyLine()
    randBG = randint(1,9)
    getImageTags = newMdl.get_imagetags()
    getImagesNew = newMdl.get_images_random(session.get("uid")) if session and "uid" in session else newMdl.get_images_random(None)
    getTags = newMdl.get_tags()
    getTotal = newMdl.count_images()

    return render_template("index.html", 
    line = randLine, bg = randBG, newImg = getImagesNew, slect = "Random", msg_color = session["msg_color"],
    imgtgs = getImageTags, kolor = kolours, tags = getTags, total = getTotal)

@app.route("/home/oldest")
def oldest():
    newMdl = mdl
    randLine = newMdl.funnyLine()
    randBG = randint(1,9)
    getImageTags = newMdl.get_imagetags()
    getImagesNew = newMdl.get_images_oldest(session.get("uid")) if session and "uid" in session else newMdl.get_images_oldest(None)
    getTags = newMdl.get_tags()
    getTotal = newMdl.count_images()

    return render_template("index.html", 
    line = randLine, bg = randBG, newImg = getImagesNew,  slect = "Oldest", msg_color = session["msg_color"],
    imgtgs = getImageTags, kolor = kolours, tags = getTags, total = getTotal)
# end home route>

# tags route
@app.route("/tags")
def viewtags():
    newMdl = mdl
    randLine = newMdl.funnyLine()
    randBG = randint(1,9)
    getImageTags = newMdl.get_imagetags()
    getTags = newMdl.get_tags()
    getTotal = newMdl.count_tags()
    return render_template("tags.html", 
    line = randLine, bg = randBG, total = getTotal,
    imgtgs = getImageTags, kolor = kolours, tags = getTags)

# search route
@app.route("/search", methods=["GET", "POST"])
def search():
    newMdl = mdl
    randLine = newMdl.funnyLine()
    randBG = randint(1,9)
    getImageTags = newMdl.get_imagetags()
    input_search = request.form["input_search"]
    uid = session.get("uid")
    getImageSpecific = newMdl.get_images_specific(input_search, uid) if uid else newMdl.get_images_specific(input_search, None)
    getTags = newMdl.get_tags()
    getTotal = newMdl.count_search_based_images(input_search)
    
    return render_template("index.html", 
    line = randLine, bg = randBG, newImg = getImageSpecific, searched = input_search, slect = "Newest",
    imgtgs = getImageTags, kolor = kolours, tags = getTags, total = getTotal)

# userpage route
@app.route("/userpage/<uname>", methods=["GET", "POST"])
def user_page(uname):
    newMdl = mdl
    randLine = newMdl.funnyLine()
    randBG = randint(1,9)
    getImageTags = newMdl.get_imagetags()
    uid = session.get("uid")
    getImageSpecific = newMdl.get_images_specific("@" + uname, uid) if uid else newMdl.get_images_specific("@" + uname, None)

    getTags = newMdl.get_tags()
    getTotal = newMdl.count_search_based_images("@" + uname)
    
    return render_template("index.html", 
    line = randLine, bg = randBG, newImg = getImageSpecific, searched = "@" + uname, slect = "Newest",
    imgtgs = getImageTags, kolor = kolours, tags = getTags, total = getTotal)

@app.route("/updoot/<int:id>", methods=["POST"])
def updoot(id):
    newMdl = mdl
    img_uid = session["uid"]
    newMdl.insert_liked(id, img_uid, dt.datetime.now())
    newMdl.update_score_plus(id)
    return "Success", 200

@app.route("/unupdoot/<int:id>", methods=["POST"])
def unupdoot(id):
    newMdl = mdl
    img_uid = session["uid"]
    newMdl.remove_liked(id, img_uid)
    newMdl.update_score_minus(id)
    return "Success", 200

@app.route("/getlikecount/<int:image_id>", methods=["GET"])
def getlikecount(image_id):
    newMdl = mdl
    like_count = newMdl.get_like_count(image_id)

    return str(like_count)

# add new image
@app.route("/save_image", methods=["POST"])
def save_image():
    newMdl = mdl
    #bagian tags db
    tag_name = request.form["tags"]
    tagid = newMdl.get_tags_latest_id()
    new_tagid = int(tagid[0]) + 1
    checkingTags = newMdl.check_tags(tag_name)
    if(checkingTags[0] == 0):
        boolVar = True
        newMdl.add_newTags(new_tagid, tag_name)
    elif(checkingTags[0] == 1):
        boolVar = False

    #bagian image db
    imgId = newMdl.get_images_latest_id()
    new_imgId = int(imgId[0]) + 1
    img_name = request.form["title"]
    img_desc = request.form["description"]
    img_image = request.files["image_file"]
    img_image2 = request.files["image_file"]
    img_uid = session.get("uid") if session.get("uid") else None
    pic = img_image.filename
    photo = pic.replace("'", "")
    foto = photo.replace("-","_")
    picture = foto.replace(" ", "_")
    if picture.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):

        # Content moderation using Clarifai
        image_filename = secure_filename(img_image.filename)  # Ensure a safe filename
        image_path = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], image_filename)  # Assuming UPLOADED_PHOTOS_DEST is your upload folder
        img_image.save(image_path)  # Save the image to the specified path
        with open(image_path, "rb") as f:
            image_content = f.read()

        clarifai_pat = PAT
        clarifai_channel = ClarifaiChannel.get_grpc_channel()
        clarifai_stub = service_pb2_grpc.V2Stub(clarifai_channel)

        clarifai_metadata = (('authorization', 'Key ' + clarifai_pat),)

        clarifai_request = service_pb2.PostModelOutputsRequest(
            user_app_id=resources_pb2.UserAppIDSet(user_id=USER_ID, app_id=APP_ID),
            model_id='moderation-recognition',
            version_id='aa8be956dbaa4b7a858826a84253cab9',
            inputs=[Input(data=Data(image=Image(base64=image_content)))]
        )

        clarifai_response = clarifai_stub.PostModelOutputs(clarifai_request, metadata=clarifai_metadata)

        if clarifai_response.status.code != status_code_pb2.SUCCESS:
            print(clarifai_response.status)
            raise Exception("Clarifai content moderation failed, status: " + clarifai_response.status.description)

        clarifai_output = clarifai_response.outputs[0]
        for concept in clarifai_output.data.concepts:
            print(f"Concept: {concept.name}, Value: {concept.value}")

        # Check if Clarifai detected any unsafe content
        if any(concept.name.lower() == 'suggestive' and concept.value > 0.7 for concept in clarifai_output.data.concepts):
            flash("Image contains suggestive content. Please upload a different image.")
            session["msg_color"] = "danger"
            return redirect(url_for("newest"))

        elif any(concept.name.lower() == 'explicit' and concept.value > 0.7 for concept in clarifai_output.data.concepts):
            flash("Image contains explicit content. Please upload a different image.")
            session["msg_color"] = "danger"
            return redirect(url_for("newest"))

        elif any(concept.name.lower() == 'drug' and concept.value > 0.7 for concept in clarifai_output.data.concepts):
            flash("Image contains drug content. Please upload a different image.")
            session["msg_color"] = "danger"
            return redirect(url_for("newest"))

        elif any(concept.name.lower() == 'gore' and concept.value > 0.7 for concept in clarifai_output.data.concepts):
            flash("Image contains gore content. Please upload a different image.")
            session["msg_color"] = "danger"
            return redirect(url_for("newest"))
                              
        # saving the image
        save_photo = photos.save(img_image2, name=picture)
        if save_photo:
            newMdl.add_newImages(new_imgId, img_name, img_desc, img_uid, picture, dt.datetime.now())
        else:
            flash("Failed to save image.")
            session["msg_color"] = "danger"
            return redirect(url_for("newest"))
    else:
        flash("Wrong file type!")
        session["msg_color"] = "danger"
        return redirect(url_for("newest"))

    #bagian image_tags db
    if(boolVar == False):
        spec_tagid = newMdl.get_tags_specific(tag_name)
        if(newMdl.add_newImgTgs(new_imgId, spec_tagid[0])):
            session["msg_color"] = "success"
            flash("Image has been added.")
            return redirect(url_for("newest", msg_color = "success"))
        else:
            session["msg_color"] = "warning"
            flash("Something went wrong. Sorry for the inconviniences.")
            return redirect(url_for("newest"))
    else:
        if(newMdl.add_newImgTgs(new_imgId, new_tagid)):
            session["msg_color"] = "success"
            flash("Image has been added.")
            return redirect(url_for("newest"))
        else:
            session["msg_color"] = "warning"
            flash("Something went wrong. Sorry for the inconviniences.")
            return redirect(url_for("newest"))

# edit image
@app.route("/save_edited_image", methods=["POST"])
@require_api_token
def save_edited_image():
    #bagian tags db
    newMdl = mdl
    tag_name = request.form["tags"]
    tagid = newMdl.get_tags_latest_id()
    new_tagid = int(tagid[0]) + 1
    checkingTags = newMdl.check_tags(tag_name)
    if(checkingTags[0] == 0):
        boolVar = True
        newMdl.add_newTags(new_tagid, tag_name)
    elif(checkingTags[0] == 1):
        boolVar = False

    #bagian image db
    imgId = request.form["edit_this"]
    img_name = request.form["title"]
    img_desc = request.form["description"]
    if(newMdl.edit_newImages(imgId, img_name, img_desc)):
        pass
    else:
        flash("Something went wrong! Sorry for the inconviniences.")
        session["msg_color"] = "danger"
        return redirect(url_for("newest"))

    #bagian image_tags db
    if(boolVar == False):
        spec_tagid = newMdl.get_tags_specific(tag_name)
        if(newMdl.edit_newImgTgs(imgId, spec_tagid[0])):
            session["msg_color"] = "success"
            flash("Image has been edited.")
            return redirect(url_for("newest"))
        else:
            session["msg_color"] = "warning"
            flash("Something went wrong. Sorry for the inconviniences.")
            return redirect(url_for("newest"))
    else:
        if(newMdl.edit_newImgTgs(imgId, new_tagid)):
            session["msg_color"] = "success"
            flash("Image has been edited.")
            return redirect(url_for("newest"))
        else:
            session["msg_color"] = "warning"
            flash("Something went wrong. Sorry for the inconviniences.")
            return redirect(url_for("newest"))

# delete an image when admin
@app.route("/sayonara_image", methods=["POST"])
@require_api_token
def sayonara_image():
    newMdl = mdl
    id = request.form["del_this"]
    #newMdl.delete_imageTag(id)
    newMdl.delete_image(id)
    session["msg_color"] = "success"
    flash("The image are deleted!")
    return redirect(url_for("newest"))

#index hanya tags
@app.route("/t/<int:tags>")
def tags(tags):
    newMdl = mdl
    randLine = newMdl.funnyLine()
    randBG = randint(1,9)
    getImageTags = newMdl.get_imagetags()
    uid = session.get("uid")
    getImageSpecific = newMdl.get_tags_based_image(tags, uid) if uid else newMdl.get_tags_based_image(tags, None)

    getTags = newMdl.get_tags()
    getTotal = newMdl.count_tags_based_images(tags)

    return render_template("index.html", 
    line = randLine, bg = randBG, newImg = getImageSpecific, total = getTotal, slect = "Newest",
    imgtgs = getImageTags, kolor = kolours, tags = getTags)

#index hanya sesuai user
@app.route("/posts")
@require_api_token
def posts():
    newMdl = mdl
    randLine = newMdl.funnyLine()
    randBG = randint(1,9)
    getImageTags = newMdl.get_imagetags()
    input_search = "@" + session["uname"]
    getImageSpecific = newMdl.get_images_specific(input_search, session["uid"])
    getTags = newMdl.get_tags()
    getTotal = newMdl.count_search_based_images(input_search)
    
    return render_template("index.html", 
    line = randLine, bg = randBG, newImg = getImageSpecific, searched = "user " + session["uname"], slect = "Newest",
    imgtgs = getImageTags, kolor = kolours, tags = getTags, total = getTotal)


@app.route("/fav")
@require_api_token
def fav():
    newMdl = mdl
    randLine = newMdl.funnyLine()
    randBG = randint(1,9)
    getImageTags = newMdl.get_imagetags()
    input_search = "@" + session["uname"]
    getImageFav = newMdl.get_images_fav(session["uid"])
    getTags = newMdl.get_tags()
    getTotal = newMdl.count_search_based_images(input_search)
    
    return render_template("index.html", 
    line = randLine, bg = randBG, newImg = getImageFav, searched = "user " + session["uname"], slect = "Newest",
    imgtgs = getImageTags, kolor = kolours, tags = getTags, total = getTotal)

@app.route("/history")
@require_api_token
def history():
    newMdl = mdl
    randLine = newMdl.funnyLine()
    randBG = randint(1,9)
    getImageTags = newMdl.get_imagetags()
    input_search = "@" + session["uname"]
    getImageHist = newMdl.get_recent_opened_image(session["uid"])
    getTags = newMdl.get_tags()
    getTotal = newMdl.count_search_based_images(input_search)
    
    return render_template("index.html", 
    line = randLine, bg = randBG, newImg = getImageHist, searched = "user " + session["uname"], slect = "Newest",
    imgtgs = getImageTags, kolor = kolours, tags = getTags, total = getTotal)

#route ke page image detail
@app.route("/i/<int:im_id>")
def images(im_id):
    newMdl = mdl
    randLine = newMdl.funnyLine()
    randBG = randint(1,9)
    getImageTags = newMdl.get_imagetags()
    getImageSpecific = newMdl.get_id_based_image(im_id)
    uid = session.get("uid")
    getImagesNew = newMdl.get_images_newest(uid) if uid is not None else newMdl.get_images_newest(None)

    getTags = newMdl.get_tags()
    getComments = newMdl.get_comments(im_id)
    sumComments = newMdl.sum_comments(im_id)
    uid = session.get("uid")
    newMdl.insert_recent_opened_image(uid, im_id, dt.datetime.now()) if uid is not None else newMdl.insert_recent_opened_image(None, im_id, dt.datetime.now())

    
    return render_template("images.html", 
    line = randLine, bg = randBG, newImg = getImagesNew, specImg = getImageSpecific,
    imgtgs = getImageTags, kolor = kolours, tags = getTags, comments = getComments, sumcmnt = sumComments)

#add comment
@app.route('/add_comment', methods=['POST'])
def add_comment():
    if request.method == 'POST':
        image_id = request.form['image_id']
        user_id = session.get("uid")  # Assuming you have user authentication
        comment_text = request.form['comment_text']
        comment_date = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Insert comment into the database
        newMdl = mdl
        newMdl.add_comment(image_id, user_id, comment_text, comment_date)

    return redirect(url_for('images', im_id=image_id))  # Redirect to the images route or wherever appropriate

#############################################################################################################
#DASHBOARD
#############################################################################################################

## bagian user data
@app.route("/dashboard/user")
@require_api_token
def user_data():
    newMdl = mdl
    randLine = newMdl.funnyLine()
    get_users = newMdl.get_user_data()
    getTotal = newMdl.count_images()
    randBG = randint(1,9)

    return render_template("/dashboard/user/data.html", users = get_users, bg = randBG,
    line = randLine, msg_color = session["msg_color"], total = getTotal)

@app.route("/dashboard/sayonara_emp", methods=["POST"])
def sayonara_user():
    newMdl = mdl
    id = request.form["del_this"]
    newMdl.sayonara_user(id)
    session["msg_color"] = "success"
    flash("The data are deleted!")
    return redirect(url_for("user_data"))
    
## bagian image data
@app.route("/dashboard/image")
@require_api_token
def image_data():
    newMdl = mdl
    randLine = newMdl.funnyLine()
    get_images = newMdl.get_images_id_order()
    getTotal = newMdl.count_images()
    randBG = randint(1,9)

    return render_template("/dashboard/image/data.html", images = get_images, bg = randBG,
    line = randLine, msg_color = session["msg_color"], total = getTotal)

if __name__ == "__main__":
    app.before_first_request(clear_session_on_startup)
    app.run(debug = True)