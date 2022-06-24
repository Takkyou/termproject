from pymongo import MongoClient
import certifi

ca = certifi.where()
client = MongoClient('mongodb+srv://test:sparta@cluster0.3m1tl.mongodb.net/Cluster0?retryWrites=true&w=majority',
                     tlsCAFile=ca)
db = client.db

import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'termproject'


@app.route('/')
def home():
    return render_template('mainpage.html')


@app.route('/moreinfo')
def moreinfo():
    return render_template('moreinfo.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')


@app.route('/news')
def news():
    return render_template('news.html')


@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/detailpage')
def detail():
    return render_template('detailpage.html')


@app.route('/mypage')
def mypage():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})
        return render_template('mypage.html', user_info=user_info)

    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route('/register', methods=['GET'])
def listing():
    information = list(db.info.find({}, {'_id': False}))
    return jsonify({'all_information': information})


@app.route('/myplayerregister', methods=['GET'])
def listing1():
    information = list(db.information1.find({}, {'_id': False}))
    return jsonify({'all_information': information, 'msg': '성공'})


@app.route('/removeplayer', methods=['POST'])
def removeplayer():
    number_receive = request.form['number_give']
    db.information1.delete_one({'no': number_receive})
    return jsonify({'msg': '삭제되었습니다', 'number': number_receive})


@app.route('/register', methods=['POST'])
def saving():
    name_receive = request.form['name_give']
    nation_receive = request.form['nation_give']
    info_receive = request.form['info_give']

    file = request.files["file_give"]

    extension = file.filename.split('.')[-1]
    today = datetime.now()
    mytime = today.strftime('%Y-%m-%d-%H-%M-%S')
    filename = f'file-{mytime}'

    save_to = f'static/{filename}.{extension}'
    file.save(save_to)

    info1 = list(db.information1.find({}, {'_id': False}))
    count = len(info1) + 1
    doc = {
        'name': name_receive,
        'no': count,
        'nation': nation_receive,
        'info': info_receive,
        'file': f'{filename}.{extension}'
    }

    db.information1.insert_one(doc)

    return jsonify({'msg': '저장이 완료되었습니다!'})

@app.route('/matching',methods=['GET'])
def matching():
    match = list(db.match.find({}, {'_id': False}))
    return jsonify({'matches': match})

@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.user.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})


@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    nickname_receive = request.form['nickname_give']
    birth_receive = request.form['birth_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,  # 아이디
        "password": password_hash,  # 비밀번호
        "profile_name": username_receive,  # 프로필 이름 기본값은 아이디
        "name": nickname_receive,
        "birth": birth_receive,
    }
    db.user.insert_one(doc)

    return jsonify({'result': 'success'})


@app.route('/sign_in', methods=['POST'])
def sign_in():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.user.find_one({'username': username_receive, 'password': pw_hash})

    if result is not None:
        payload = {
            'id': username_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')

        return jsonify({'result': 'success', 'token': token})

    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


@app.route('/searching_in', methods=['POST'])
def searching_nationplayer():
    nation_receive = request.form['searching_give']
    team = list(db.info1.find({'Nation': nation_receive}, {'_id': False}))
    player = list(db.info1.find({'Player': nation_receive}, {'_id': False}))
    return jsonify({'team': team, 'player': player})

#admin

@app.route('/InsertMainPlayer', methods=['POST'])
def InsertPlayer():
    player_receive = request.form['Player_give']
    nation_receive = request.form['Nation_give']
    group_receive = request.form['Group_give']
    no_receive = request.form['No_give']
    pos_receive = request.form['Pos_give']
    age_receive = request.form['Age_give']
    Amatchcaps_receive = request.form['Amatchcaps_give']
    Amatchgoals_receive = request.form['Amatchgoals_give']
    Club_receive = request.form['Club_give']
    Image_url_receive = request.form['Image_url_give']

    doc = {
        "Nation" : nation_receive,
        "GROUP" : group_receive,
        "No" : no_receive,
        "Pos" : pos_receive,
        "Player" : player_receive,
        "Age" : age_receive,
        "A match caps" : Amatchcaps_receive,
        "A match goals" : Amatchgoals_receive,
        "Club" :Club_receive,
        "image_url" : Image_url_receive,
    }

    db.info1.insert_one(doc)

    return jsonify({'msg':"insert 완료"})

@app.route('/UpdateMainPlayer', methods=['POST'])
def UpdatePlayer():
    player_receive = request.form['Player_give']
    nation_receive = request.form['Nation_give']
    group_receive = request.form['Group_give']
    no_receive = request.form['No_give']
    pos_receive = request.form['Pos_give']
    age_receive = request.form['Age_give']
    Amatchcaps_receive = request.form['Amatchcaps_give']
    Amatchgoals_receive = request.form['Amatchgoals_give']
    Club_receive = request.form['Club_give']
    Image_url_receive = request.form['Image_url_give']


    db.info1.update_one({'Player':player_receive},{"$set":{
        "Nation": nation_receive,
        "GROUP": group_receive,
        "No": no_receive,
        "Pos": pos_receive,
        "Age": age_receive,
        "A match caps": Amatchcaps_receive,
        "A match goals": Amatchgoals_receive,
        "Club": Club_receive,
        "image_url": Image_url_receive,}})
    return jsonify({'msg': "update 완료"})

@app.route('/DeleteMainPlayer', methods=['POST'])
def DeletePlayer():
    player_receive = request.form['Player_give']

    db.info1.delete_one({'Player':player_receive})

    return jsonify({'msg':'delete 성공! '})

@app.route('/UpdateI', methods=['POST'])
def UpdateInfo():
    player = request.form['player_give1']

    a = list(db.info1.find({"Player":player}, {'_id': False}))

    return jsonify({'msg':'불러오기 성공!','info': a})




if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
