# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from flask import Flask,request,Response
import leancloud
import uuid
import os
import json

APP_ID = os.environ['LC_APP_ID']
MASTER_KEY = os.environ['LC_APP_MASTER_KEY']

app = Flask(__name__)
leancloud.init(APP_ID,master_key=MASTER_KEY)

@app.route("/", methods = ['GET','POST'])
def index():
    if request.method == 'GET':
        return "Hi!"
    email = request.json.get("email")
    user_query = leancloud.Query('_User')
    user_query.equal_to("username",email)
    if user_query.count() == 0:
        pawd = uuid.uuid4().hex
        user = leancloud.User()
        user.sign_up(email, pawd)
        return pawd
    r = Response('该账号已存在')
    r.status_code = 403
    return r

@app.route("/submit",methods=['POST'])
def score():
    f = request.json
    email = f.get('email')
    pawd = f.get('password')
    u = leancloud.User()
    try:
        u.login(email, pawd)
    except leancloud.LeanCloudError as e:
        r = Response(e.message)
        r.status_code = 500
        print e
        return r
    u.set(f.get("quizName"), f.get("final"))
    r = u.relation("codebase")
    q = r.query.equal_to("quizName", f.get("quizName"))
    if q.count() == 0:
        C = leancloud.Object.extend("codebase")
        code = C()
        code.set("quizName", f.get("quizName"))
        code.set("code", f.get("code"))
        code.set("result", f.get("result"))
        code.save()
        r.add(code)
        u.save()
    else:
        code = q.first()
        code.set("code", f.get("code"))
        code.set("result", f.get("result"))
        code.save()
    return "提交成功"





