from inspect import getfile
from flask import Flask, redirect, render_template, request, url_for, session, flash, make_response #belum ada flash di htmlnya
from random import *
from functools import wraps
from model import Model as mdl
from flask_uploads import UploadSet, configure_uploads, IMAGES
import jwt
import datetime as dt
from werkzeug.datastructures import FileStorage

app = Flask(__name__)
app.config["SECRET_KEY"] = "123"

app.config['UPLOADED_PHOTOS_DEST'] = 'static/img'
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)

kolours = ["rgb(25, 62, 68, 0.95)", "rgb(99, 56, 117, 0.95)",
    "rgb(0, 130, 97, 0.95)", "rgb(200, 109, 75, 0.95)", "rgb(38, 59, 167, 0.95)",
    "rgb(118, 40, 40, 0.95)", "rgb(80, 32, 123, 0.95)", "rgb(77, 84, 154, 0.95)",
    "rgb(183, 92, 103, 0.95)", "rgb(18, 149, 166, 0.95)"]

# fungsi jwt dan session
def require_api_token(func):
    @wraps(func)
    def check_token(*args, **kwargs):
        if 'api_session_token' not in session:
            return redirect(url_for("newest"))
        try:
            data = jwt.decode(session["api_session_token"], app.config["SECRET_KEY"])
        except:
            session["msg_color"] = "warning"
            flash("Token Expired")
            return redirect(url_for("newest"))
        return func(*args, **kwargs)

    return check_token

#############################################################################################################
#PICTUREFY PAGES
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
    if(pwd == repwd):
        checking_uname = newMdl.check_username(uname)
        checking_email = newMdl.check_email(email)
        if(checking_uname[0][0] == 0):
            if(checking_email[0][0] == 0):
                if(newMdl.registering(uname, pwd, dt.datetime.now(), 0, email)):
                    session["msg_color"] = "success"
                    flash("Sign Up Success!")
                    return redirect(url_for("login"))
                else:
                    session["msg_color"] = "danger"
                    flash("Something's Wrong! Sorry fo the inconveniences.")
                    return redirect(url_for("register"))
            else:
                session["msg_color"] = "warning"
                flash("Someone already used the Email.")
                return redirect(url_for("register"))  
        else:
            session["msg_color"] = "warning"
            flash("Username is not correct.")
            return redirect(url_for("register"))            
    else:
        session["msg_color"] = "warning"
        flash("Password must be same!")
        return redirect(url_for("register"))

# login page route
@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/loggin_in", methods=["POST"])
def loggin_in():
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
    session["uid"] = None
    session["msg_color"] = "secondary"
    return redirect(url_for("newest"))

@app.route("/home/newest")
def newest():
    newMdl = mdl
    randLine = newMdl.funnyLine()
    randBG = randint(1,9)
    getImageTags = newMdl.get_imagetags()
    getImagesNew = newMdl.get_images_newest(session["uid"])
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
    getImagesNew = newMdl.get_images_random(session["uid"])
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
    getImagesNew = newMdl.get_images_oldest(session["uid"])
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
    getImageSpecific = newMdl.get_images_specific(input_search, session["uid"])
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
    getImageSpecific = newMdl.get_images_specific("@" + uname, session["uid"])
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
    img_uid = session["uid"]
    pic = img_image.filename
    photo = pic.replace("'", "")
    foto = photo.replace("-","_")
    picture = foto.replace(" ", "_")
    if picture.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
        save_photo = photos.save(img_image, name=picture)
        if save_photo:
            newMdl.add_newImages(new_imgId, img_name, img_desc, img_uid, picture, dt.datetime.now())
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
    newMdl.delete_imageTag(id)
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
    getImageSpecific = newMdl.get_tags_based_image(tags, session["uid"])
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
    getImageSpecific = newMdl.get_user_based_image(session["uname"], session["uid"])
    getTags = newMdl.get_tags()
    getTotal = newMdl.count_user_based_images(session["uid"])

    return render_template("index.html", 
    line = randLine, bg = randBG, newImg = getImageSpecific, total = getTotal, slect = "Newest",
    imgtgs = getImageTags, kolor = kolours, tags = getTags, searched = "user " + session["uname"])

#route ke page image detail
@app.route("/i/<int:im_id>")
def images(im_id):
    newMdl = mdl
    randLine = newMdl.funnyLine()
    randBG = randint(1,9)
    getImageTags = newMdl.get_imagetags()
    getImageSpecific = newMdl.get_id_based_image(im_id)
    getImagesNew = newMdl.get_images_newest(session["uid"])
    getTags = newMdl.get_tags()
    
    return render_template("images.html", 
    line = randLine, bg = randBG, newImg = getImagesNew, specImg = getImageSpecific,
    imgtgs = getImageTags, kolor = kolours, tags = getTags)


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
    app.run(debug = True)