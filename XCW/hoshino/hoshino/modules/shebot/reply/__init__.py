import re
from os import path
from hoshino.service import Service
import sqlite3
from collections import defaultdict
from random import choice


_dbpath = path.join(path.dirname(__file__), 'reply.db3')

class SqlTable:
    conn = sqlite3.connect(_dbpath)
    cur = conn.cursor()
    def __init__(self, db_path: str, table_name: str) -> None:
        self.table = table_name

    def select(self) -> dict:
        SqlTable.cur.execute(f'select * from {self.table}')
        rows = SqlTable.cur.fetchall()
        return {r[0]:list(set(r[1].split('|'))) for r in rows}

    def insert(self, word: str, reply: str) -> None:
        SqlTable.cur.execute(f'insert into {self.table} (word, reply) values(?, ?)', [word, reply])
        SqlTable.conn.commit()

    def update(self, word: str, reply: str) -> None:
        SqlTable.cur.execute(f'update {self.table} set reply = ? where word = ?', [reply, word])
        SqlTable.conn.commit()

    def delete(self, word: str) -> None:
        self.cur.execute(f'delete from {self.table} where word = ?', [word])
        self.conn.commit()

    def __del__(self) -> None:
        print('close database')
        SqlTable.conn.commit()
        self.conn.close()

class BaseHandler:

    def __init__(self, table_name) -> None:
        self.sqltable = SqlTable(_dbpath, table_name)
        self._dict = self.sqltable.select() or defaultdict(list)
    
    def add(self, x: str, reply: str) -> None:
        raise  NotImplementedError

    def delete(self, x: str) -> None:
        if x in self._dict:
            del self._dict[x]
            self.sqltable.delete(x)
        else:
            raise ValueError('不存在的关键字')

    def find_reply(self, event) -> str:
        raise NotImplementedError
 

class FullmatchHandler(BaseHandler):
    def __init__(self) -> None:
        super().__init__('fullmatch')

    def add(self, word: str, reply: str) -> None:
        if word in self._dict:
            if reply in self._dict[word]:
                raise ValueError('该回复已经存在，无需重复添加') 
            self._dict[word].append(reply)
            #将集合元素以|连接后存入数据库
            reply_str = '|'.join(self._dict[word])
            self.sqltable.update(word, reply_str)
        else:
            self._dict[word] = list(reply.split('|'))
            self.sqltable.insert(word, reply)
            
    def find_reply(self, event) -> str:
        msg = event.raw_message.strip()
        replys = self._dict.get(msg)
        if replys:
            return choice(replys)
        else:
            return None


class KeywordHandler(BaseHandler):
    def __init__(self) -> None:
        super().__init__('keyword')

    def add(self, keyword: str, reply: str) -> None:
        if keyword in self._dict:
            self._dict[keyword].append(reply)
            reply_str = '|'.join(self._dict[keyword])
            self.sqltable.update(keyword, reply_str)
            return
        for k in self._dict:
            if keyword in k or k in keyword:
                raise ValueError('关键字冲突')
        self._dict[keyword] = list(reply.split('|'))
        self.sqltable.insert(keyword, reply)

    def find_reply(self, event) -> str:
        msg = event.raw_message.strip()
        for k in self._dict:
            if k in msg:
                return choice(self._dict[k]) 
        return None

class RexHandler(BaseHandler):
    def __init__(self) -> None:
        super().__init__('rex')

    def add(self, pattern: str, reply: str) -> None:
        self._dict[pattern] = list(reply.split('|'))
        self.sqltable.insert(pattern, reply)

    def find_reply(self, event) -> str:
        msg = event.raw_message.strip()
        for pattern in self._dict:
            match = re.search(pattern, msg)
            if match:
                reply = choice(self._dict[pattern])
                return reply


fullmatch = FullmatchHandler()
keyword = KeywordHandler()
rex = RexHandler()
chain = [fullmatch, keyword, rex]

import nonebot
bot = nonebot.get_bot()
@bot.on_message()
async def reply(ctx):
    for h in chain:
        reply = h.find_reply(ctx)
        if reply:
            await bot.send(ctx, reply)
            return
    else:
        pass

sv = Service('自定义问答', use_priv=999)
from hoshino.util4sh import Res
@sv.on_rex(r'((?:fullmatch)|(?:keyword)|(?:rex)).{1,200}#.{1,200}')
async def add_reply(bot, event):
    await Res.save_image(event)
    match = event['match']
    handler = match.group(1)
    word, reply = tuple(event.raw_message.strip(handler).strip().split('#'))
    try:
        eval(handler).add(word, reply)
        await bot.send(event, '添加成功')
    except Exception as ex:
        sv.logger.error(f'添加失败{ex}')
        await bot.send(event, f'添加失败，{ex}')

@sv.on_rex(r'删除((?:fullmatch)|(?:keyword)|(?:rex))(.+)')
async def delete_reply(bot, event):
    match = event['match']
    handler = match.group(1)
    word = match.group(2)
    try:
        eval(handler).delete(word)
        await bot.send(event, '删除成功')
    except ValueError as vr:
        sv.logger.error(vr)
        await bot.send(event, f'删除失败,{vr}')