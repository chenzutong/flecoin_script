import os
import json
import sqlite3
import time
import operator

from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request
from flask_cors import CORS

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Command(db.Model):
    __tablename__ = 'command'
    id = db.Column(db.String(128), primary_key=True)
    name = db.Column(db.String(128), unique=True)
    position = db.Column(db.String(128), unique=True)
    subset = db.Column(db.Text)


db.create_all()


@app.route('/')
def hello_world():
    with open("./index.md", 'r') as file:
        message = file.read()
    return message


def sort_cmd(n, arr):
    cmdDict = {}
    if not arr:
        return []
    for r in arr:
        position = r["position"]
        position_num = position.split("-")[n]
        if not position_num in cmdDict:
            cmdDict[position_num] = []
        cmdDict[position_num].append(r)
    cmdList = list(cmdDict.values())
    cmdList2 = []
    for c in cmdList:
        if len(cmdList) == 1:
            cmdList2.append(c)
        cmdList2.append(sort_cmd2(c))
    return cmdList2


def sort_cmd2(arr):
    masterDic = {}
    otherlist = []
    otherlist2 = []
    for r in arr:
        position = r["position"]
        position_num = position.split("-")
        if len(position_num) == 1:
            masterDic = r
            arr.remove(r)
            break
    for r in arr:
        position = r["position"]
        position_num = position.split("-")
        if len(position_num) != 2:
            otherlist2.append(r)
        else:
            otherlist.append(r)
    if otherlist2:
        for r in otherlist2:
            position = r["position"]
            position_r = position.split("-")
            for i, val in enumerate(otherlist):
                position = val["position"]
                position_i = position.split("-")
                if position_r[1] == position_i[1]:
                    val["subset"].append(r)
                    val["subset"] = sort_cmd3(val["subset"])
                    otherlist[i] = val

    masterDic["subset"] = otherlist
    return masterDic


def sort_cmd3(arr):
    masterDic = {}
    otherlist = []
    otherlist2 = []
    for r in arr:
        position = r["position"]
        position_num = position.split("-")
        if len(position_num) != 3:
            otherlist.append(r)
        else:
            otherlist2.append(r)
    if not otherlist:
        return arr
    else:
        for r in otherlist:
            position = r["position"]
            position_r = position.split("-")
            for i, val in enumerate(otherlist2):
                position = val["position"]
                position_i = position.split("-")
                if position_r[2] == position_i[2]:
                    val["subset"].append(r)
                    otherlist2[i] = val
    return otherlist2


@app.route('/list')
def get_list():
    cmdList = []
    for r in Command.query.all():
        position_num = r.position.split("-")
        pos = int(position_num[0])*10000
        if len(position_num) == 2:
            pos = int(position_num[1]) * 100 + pos
        if len(position_num) == 3:
            pos = int(position_num[1]) * 100 + int(position_num[2]) + pos

        if len(position_num) == 4:
            pos = int(position_num[1]) * 100 + int(position_num[2]) + int(position_num[3]) + pos
        res = {"id": r.id, "name": r.name, "position": r.position, "pos": pos, "subset": []}
        cmdList.append(res)
    sorted_x = sorted(cmdList, key=operator.itemgetter('pos'))
    cmdList = sort_cmd(0, sorted_x)
    j = json.dumps({"subset": cmdList})
    return j


@app.route('/find_cmd/<cmd_id>')
def find_cmd(cmd_id):
    get_cmd = Command.query.filter_by(id=cmd_id).first()
    res = {"id": get_cmd.id, "name": get_cmd.name, "position": get_cmd.position}
    return json.dumps(res)


@app.route('/find_md/<cmd_id>')
def find_md(cmd_id):
    print(cmd_id)
    try:
        get_cmd = Command.query.filter_by(id=cmd_id).first()
        print(get_cmd)
        print(type(get_cmd))
        name = get_cmd.name.replace(' ', '')
    except Exception as e:
        print(e)
        return "错误"
    # 读取配置文件
    with open("./{}.md".format(name), 'r') as file:
        message = file.read()
    return message


@app.route('/delete_cmd/<cmd_id>')
def delete_cmd(cmd_id):
    try:
        print(cmd_id)
        conn = sqlite3.connect('data.sqlite')
        cursor = conn.cursor()
        cursor.execute('delete from command where id = ?', (cmd_id,))
        cursor.close()
        conn.commit()
        conn.close()
        # remove_cmd = Command.query.filter_by(id=cmd_id).delete()
        # print(remove_cmd)
        # db.session.delete(remove_cmd)
        # db.session.commit()
        # db.session.execute('delete from command where id = ?', (cmd_id, ))
        # Command.query.filter_by(id=cmd_id).delete()
    except Exception as e:
        return str(e)

    return "ok"


@app.route('/update_cmd/<cmd_id>', methods=["POST"])
def update_cmd(cmd_id):
    updateCmd = Command.query.filter_by(id=cmd_id).first()
    print(updateCmd.name)
    req = request.values
    print(req)
    name = req['name'] if 'name' in req else ''
    tempName = updateCmd.name
    if name:
        updateCmd.name = name
    position = req['position'] if 'position' in req else ''
    if position:
        updateCmd.position = position
    # db.session.add(updateCmd)
    try:
        db.session.commit()
    except Exception as e:
        print(e)
    else:
        if name:
            tempName = tempName.replace(' ', '')
            name = name.replace(' ', '')
            os.popen("mv {}.md {}.md".format(tempName, name))
    return "ok"


@app.route('/update/<cmd_id>', methods=["POST"])
def update_md(cmd_id):
    req = request.values
    print(req)
    get_cmd = Command.query.filter_by(id=cmd_id).first()
    print(get_cmd)
    name = get_cmd.name.replace(' ', '')
    text = req['text'] if 'text' in req else ''
    with open("./{}.md".format(name), "w", encoding="utf-8") as file:
        file.write(text)
    return "ok"


@app.route('/add_cmd', methods=["POST"])
def add_cmd():
    req = request.values
    print(req)
    name = req['name'] if 'name' in req else ""
    position = req['position'] if 'position' in req else ''
    #
    position_num = position.split("-")
    for q in position_num:
        try:
            q = int(q)
        except:
            return "添加位置编号格式错误"
        if type(q) != int:
            print(type(q))
            return "添加位置编号格式错误1"

    if not name or not position:
        return "请输入完整"
    rn = Command.query.filter_by(name=name).all()
    if rn:
        return "已有命令"
    rs = Command.query.filter_by(position=position).all()
    if rs:
        return "位置已有命令"
    id = str(time.time())
    subset = ""
    new_cmd = Command(id=id, name=name, position=position, subset=subset)
    db.session.add(new_cmd)
    db.session.commit()
    namer = name.replace(' ', '')
    os.popen("echo '## {}' >{}.md".format(name, namer)).read()
    return id


if __name__ == '__main__':
    app.debug = True
    CORS(app, supports_credentials=True)
    app.run(host="0.0.0.0", port=7777)