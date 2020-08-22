import json
import os
from .data_source import render_template, static_folder
from quart import request, session, redirect, url_for,send_from_directory
from ..reply import fullmatch, rex, keyword
from os import path
from hoshino.util4sh import Res as R
from quart import Blueprint

reply = Blueprint('reply', __name__, static_folder='/static')

@reply.route('/staticfile/<filename>')
async def staticfile(filename):
    return await send_from_directory(static_folder, filename)

@reply.route('/reply/show/')
async def show_reply():
    url = f'{public_address}:{port}'
    return await render_template('show_reply.html', url = url, url_for = url_for)

@reply.route('/reply/api/<action>', methods=['GET', 'POST'])
async def call_action(action: str):
    data = await request.get_data()
    _triggers = {
        '完全匹配' : 'fullmatch',
        '关键字匹配' : 'keyword',
        '正则匹配' : 'rex'
    }

    if action == 'show':
        f_dic = fullmatch.sqltable.select()
        k_dic = keyword.sqltable.select()
        r_dic = rex.sqltable.select()
        reply_list = [{'trigger':'完全匹配', 'word':k, 'reply':'|'.join(v) } for k,v in f_dic.items()]
        reply_list.extend([{'trigger':'关键字匹配', 'word':k, 'reply':'|'.join(v) } for k,v in k_dic.items()])
        reply_list.extend([{'trigger':'正则匹配', 'word':k, 'reply':'|'.join(v) } for k,v in r_dic.items()])
        return {
            "data" : reply_list
        }

    elif action == 'delete':
        data = json.loads(data.decode())
        word = data['word']
        trigger = data['trigger']
        eval(_triggers[trigger]).delete(word)
        return 'success'

    elif action == 'add':
        data = json.loads(data.decode())
        trigger = data['trigger']
        word = data['word']
        reply = data['reply']
        eval(trigger).add(word, reply)
        return 'success'

    elif action == 'upload':
        fs = await request.files
        fobj = fs.get('file')
        f_type = fobj.content_type
        if f_type.startswith('image'):
            folder = R.image_dir
            if not path.exists(folder):
                os.mkdir(folder)
            with open(path.join(folder, fobj.filename), 'wb') as f:
                f.write(fobj.read())
            print(str(R.image(fobj.filename)))
            return str(R.image(fobj.filename))
        elif f_type.startswith('audio'):
            folder = R.record_dir
            folder = R.image_dir
            if not path.exists(folder):
                os.mkdir(folder)
            with open(path.join(folder, fobj.filename), 'wb') as f:
                f.write(fobj.read())
            return str(R.record(fobj.filename))
        else:
            raise TypeError('不支持的文件类型')

import nonebot
from datetime import timedelta

app = nonebot.get_bot().server_app
public_address = 'xxx.xx.xx.xx' #改为你服务器的公网ip
port = nonebot.get_bot().config.PORT
passwd = '123456' #登录密码
@reply.before_request
async def _():
    user_ip = request.remote_addr
    if request.path == '/login':
        return
    if session.get('user_ip') == user_ip:#登录过
        return
    #没有登录，重定向至登录界面
    return redirect('/login') 

@reply.route('/login',methods=['GET','POST'])
async def login():
    print(request.method)
    if request.method == 'GET':
        return await render_template('login.html',passwd=passwd,public_address=public_address,port=port)
    else:
        login_data = await request.form
        input_psd = login_data.get('password')
        if input_psd == passwd:
            user_ip = request.remote_addr
            session['user_ip'] = user_ip
            session.permanent = True
            app.permanent_session_lifetime = timedelta(weeks=2)
            return redirect('/reply/show')
        else:
            return redirect('/login')




