from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify
from database import DBhandler
import hashlib
import sys

application = Flask(__name__)
application.config["SECRET_KEY"] = "helloosp"
DB = DBhandler()

@application.route("/")
def hello():
    return render_template("top.html")
    #return redirect(url_for('view_list'))

@application.route("/login")
def login():
    return render_template("seven_login.html")

@application.route("/logout")
def logout_user():
    session.clear()
    return render_template("index.html")

@application.route("/mypage")
def view_mypage():
    return render_template("mypage.html")

@application.route("/signup")
def view_signup():
    return render_template("signup.html")

@application.route("/login_confirm", methods=['POST'])
def login_user():
    id_ = request.form['id']
    pw = request.form['pw']
    pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()
    
    if DB.find_user(id_, pw_hash):
        session['id'] = id_
        #return redirect(url_for('view_list'))
        return render_template("two_item.html")
    else:
        flash("Wrong ID or PW!")
        return render_template("login.html")

@application.route("/list")
def view_list():
    page = request.args.get("page", 0, type=int)
    per_page = 6
    per_row = 3
    row_count = int(per_page/per_row)
    start_idx = per_page*page
    end_idx = per_page*(page+1)
    data= DB.get_items()
    item_counts = len(data)
    data = dict(list(data.items())[start_idx:end_idx])
    tot_count = len(data)
    for i in range(row_count):
        if (i == row_count-1) and (tot_count % per_row != 0):
            locals()['data_{}'.format(i)] = dict(list(data.items())[i*per_row:])
        else:
            locals()['data_{}'.format(i)] = dict(list(data.items())[i*per_row:(i+1)*per_row])
    
    return render_template(
        "list.html",
        datas=data.items(),
        row1=locals()['data_0'].items(),
        row2=locals()['data_1'].items(),
        limit=per_page,
        page=page,
        page_count=int((item_counts/per_page)+1),
        total=item_counts)

@application.route("/view_detail/<name>/")
def view_item_detail(name):
    print("###name:",name)
    data = DB.get_item_byname(name)
    print("####data:", data)
    return render_template("detail.html", name=name, data=data)

@application.route("/view_review_detail/<name>/")
def view_review_detail(name):
    print("###name:",name)
    data = DB.get_review_byname(name)
    #thumb = DB.get_thumb_byname(name)
    print("####data:", data)
    return render_template("six_review_detail.html", name=name, data=data)

@application.route("/review")
def view_review():
    page = request.args.get("page", 0, type=int)
    per_page=6 # item count to display per page
    per_row=1# item count to display per row
    row_count=int(per_page/per_row)
    start_idx=per_page*page
    end_idx=per_page*(page+1)
    data = DB.get_reviews() #read the table
    item_counts = len(data)
    data = dict(list(data.items())[start_idx:end_idx])
    tot_count = len(data)
    for i in range(row_count):#last row
        if (i == row_count-1) and (tot_count%per_row != 0):
            locals()['data_{}'.format(i)] = dict(list(data.items())[i*per_row:])
        else:
            locals()['data_{}'.format(i)] = dict(list(data.items())[i*per_row:(i+1)*per_row])
    
    return render_template(
     "five_review_1109.html",
     datas=data.items(),
     row1=locals()['data_0'].items(),
     row2=locals()['data_1'].items(),
     row3=locals()['data_2'].items(),
     row4=locals()['data_3'].items(),
     row5=locals()['data_4'].items(),
     row6=locals()['data_5'].items(),
     limit=per_page,
     page=page,
     page_count=int((item_counts/per_page)+1),
     total=item_counts)

@application.route("/reg_items")
def reg_item():
    return render_template("one_item_regi.html")

@application.route("/contact")
def view_contact():
    return render_template("contact.html")

@application.route("/submit_item_post", methods=['POST'])
def reg_item_submit_post():
    image_file=request.files["file"]
    image_file.save("static/images/{}".format(image_file.filename))
    data=request.form
    DB.insert_item(data['item_title'], data, image_file.filename)
    return render_template("submit_item_result.html", data=data, img_path="static/images/{}".format(image_file.filename))


@application.route("/signup_post", methods=['POST'])
def register_user():
    data=request.form
    pw=request.form['pw']
    pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()
    data_with_more_info = {
        'id' : data['id'],
        'pw' : pw_hash,
        'nickname' : data['nickname'],
        'phonenum' : data.get('phonenum', '')
    }
    if DB.insert_user(data_with_more_info):
        return render_template("login.html")
    else:
        flash("user id already exist!")
        return render_template("signup.html")
    
#@application.route('dynamicurl/<varible_name>/')
#def DynamicUrl(varible_name):
#    return str(varible_name)

@application.route("/reg_review_init/<name>/")
def reg_review_init(name):
    return render_template("four_review.html", name=name)

@application.route("/reg_review", methods=['POST'])
def reg_review():
    image_file=request.files["file"]
    image_file.save("static/images/{}".format(image_file.filename))
    data=request.form
    DB.reg_review(data, image_file.filename)
    return redirect(url_for('view_review'))

@application.route('/show_heart/<name>/', methods=['GET'])
def show_heart(name):
    my_heart = DB.get_heart_byname(session['id'],name)
    return jsonify({'my_heart': my_heart})

@application.route('/like/<name>/', methods=['POST'])
def like(name):
    my_heart = DB.update_heart(session['id'],'Y',name)
    return jsonify({'msg': '좋아요 완료!'})

@application.route('/unlike/<name>/', methods=['POST'])
def unlike(name):
    my_heart = DB.update_heart(session['id'],'N',name)
    return jsonify({'msg': '안좋아요 완료!'})

@application.route('/show_thumb/<name>/', methods=['GET'])
def show_thumb(name):
    item_thumb = DB.get_thumb_byname(name, session['id'])
    return jsonify({'item_thumb': item_thumb})

@application.route('/thumb/<name>/', methods=['POST'])
def thumb(name):
    item_thumb = DB.update_thumb(name, 'Y', session['id'])
    return jsonify({'msg': '도움이 됐어요!'})

@application.route('/unthumb/<name>/', methods=['POST'])
def unthumb(name):
    item_thumb = DB.update_thumb(name,'N', session['id'])
    return jsonify({'msg': '도움이 됐어요 취소!'})

if __name__ == "__main__":
    application.run(host='0.0.0.0', debug=True)
