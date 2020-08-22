import sqlite3
import os
import traceback
from typing import AsyncIterator

from aiocqhttp import event
from hoshino.priv import *
from nonebot.log import logger

class Record:
    def __init__(self,qu=None,ans=None,rec_maker=None,group_id=None,is_open=None):
        with sqlite3.connect(os.path.dirname(__file__)+'/records.db3') as conn:
            cur = conn.cursor()
        self.conn = conn
        self.cur = cur
        self.question = qu
        self.answer = ans
        self.rec_maker = rec_maker
        self.group_id = group_id
        self.is_open = is_open

    def __del__(self):
        self.cur.close()
        self.conn.close()

    def get_records(self):
        records = {}
        try:
            sql = f'select question,answer,rec_maker,group_id,is_open from records'
            self.cur.execute(sql)
            rows = self.cur.fetchall()
            for row in rows:
                records[row[0],row[3]] = {'answer':row[1],'rec_maker':row[2],'is_open':row[4]}
            return records
        except Exception as ex:
            logger.info(ex)
            return None
    def insert_database(self):
        try:
            sql = f'insert into records(question,answer,rec_maker,group_id,is_open)values\
            ("{self.question}","{self.answer}",{self.rec_maker},{self.group_id},{self.is_open})'
            logger.info(f'执行一条sql {sql}')
            self.cur.execute(sql)
            self.conn.commit()
            return True
        except:
            traceback.print_exc()
            return False

    def delete(self,qu,gid):
        try:
            sql = f'delete from records where question="{qu}" and group_id={gid}'
            self.cur.execute(sql)
            self.conn.commit()
            return True
        except Exception as ex:
            logger.info(ex)
            return False

    def delete_force(self,qu):
        try:
            sql = f'delete from records where question="{qu}"'
            self.cur.execute(sql)
            self.conn.commit()
            return True
        except Exception as ex:
            logger.info(ex)
            return False

    
    def count_user_records(self,uid):
        try:
            sql = f'select count(*) from records where rec_maker={uid}'
            self.cur.execute(sql)
            row = self.cur.fetchone()
            return row[0]
        except Exception as ex:
            logger.info(ex)
            return None

def get_user_quota(user_priv):
    if user_priv == SUPERUSER:
        return 999
    if user_priv == OWNER:
        return 10
    elif user_priv == ADMIN:
        return 5
    else:
        return 3

def show(records:dict,page:int):
    rec_num = len(records)
    pages = int(rec_num/5) + 1
    if page > pages:
        return None

    if pages == page:
        reply = ''
        for (k,v) in list(records.keys())[5*page-5:]:
            reply += (k+' : '+records[(k,v)]['answer']+'\n')
        return reply,pages
    else :
        reply = ''
        for (k,v) in list(records.keys())[5*page-5:5*page]:
            reply += (k+' : '+records[(k,v)]['answer']+'\n')
        return reply,pages

import nonebot
from random import choice
import asyncio
async def send_msg(event, msg, at_sender:bool=False):
    bot = nonebot.get_bot()
    replys = msg.split('|')
    reply = choice(replys)
    final_replys = reply.split('+')
    for r in final_replys:
        await bot.send(event, r, at_sender=at_sender)
        await asyncio.sleep(0.5)
    
