import time
import re
import hashlib
import os
from .data import Question
from hoshino import Service, priv, aiorequests
from hoshino.typing import CommandSession
answers = {}
sv = Service('QA',help_='''
我问你答
[我问xxx你答yyy] 我问你答,针对个人
[大家问xxx你答yyy] 针对全群（需要管理员权限）
'''.strip())
qa_path = os.path.expanduser('~/.hoshino/QA')
if not os.path.exists(qa_path):
    os.mkdir(qa_path)


def union(group_id, user_id):
    return (group_id << 32) | user_id


async def cqimage(a):
    if r'[CQ:image,' in a:
        url = re.search(r'url=([\S]*)\]', a).group(1)
        imgname = hashlib.md5(url.encode('utf8')).hexdigest()
        imgget = await aiorequests.get(url)
        imgcon = await imgget.content
        imgpath = os.path.join(qa_path, f'{imgname}.png')
        with open(imgpath, 'wb') as f:
            f.write(imgcon)
            f.close()
        a = f'[CQ:image,cache=0,file=file:///{os.path.abspath(imgpath)}]'
    return a

# recovery from database
for qu in Question.select():
    if qu.quest not in answers:
        answers[qu.quest] = {}
    answers[qu.quest][union(qu.rep_group, qu.rep_member)] = qu.answer


@sv.on_message('group')
async def setqa(bot, context):
    message = context['raw_message']
    # print(priv.get_user_priv(context))
    if message.startswith('我问'):
        msg = message[2:].split('你答', 1)
        if len(msg[1]) == 0 or len(msg[0]) == 0:
            await bot.send(context, '发送“我问xxx你答yyy”我才能记住', at_sender=False)
            return
        q, a = msg
        if 'granbluefantasy.jp' in q or 'granbluefantasy.jp' in a:
            # await bot.send(context, '骑空士还挺会玩儿？爬！\n', at_sender=True)
            return
        if q not in answers:
            answers[q] = {}
        a = await cqimage(a)
        answers[q][union(context['group_id'], context['user_id'])] = a
        Question.replace(
            quest=q,
            rep_group=context['group_id'],
            rep_member=context['user_id'],
            answer=a,
            creator=context['user_id'],
            create_time=time.time(),
        ).execute()
        await bot.send(context, f'好的我记住了', at_sender=False)
    elif message.startswith('大家问') or message.startswith('有人问'):
        if priv.get_user_priv(context) < priv.ADMIN:
            await bot.send(context, f'只有管理员才可以用{message[:3]}', at_sender=False)
            return
        msg = message[3:].split('你答', 1)
        if len(msg[1]) == 0:
            await bot.send(context, f'发送“{message[:3]}xxx你答yyy”我才能记住', at_sender=False)
            return
        q, a = msg
        a = await cqimage(a)
        if q not in answers:
            answers[q] = {}
        answers[q][union(context['group_id'], 1)] = a
        Question.replace(
            quest=q,
            rep_group=context['group_id'],
            rep_member=1,
            answer=a,
            creator=context['user_id'],
            create_time=time.time(),
        ).execute()
        await bot.send(context, f'好的我记住了', at_sender=False)
    elif message.startswith('不要回答') or message.startswith('不再回答'):
        q = context['raw_message'][4:]
        ans = answers.get(q)
        if ans is None:
            await bot.send(context, f'我不记得有这个问题', at_sender=False)
        specific = union(context['group_id'], context['user_id'])
        a = ans.get(specific)
        if a:
            Question.delete().where(
                Question.quest == q,
                Question.rep_group == context['group_id'],
                Question.rep_member == context['user_id'],
            ).execute()
            del ans[specific]
            if not ans:
                del answers[q]
            await bot.send(context, f'我不再回答"{a}"了', at_sender=False)

        if priv.get_user_priv(context) < priv.ADMIN:
            await bot.send(context, f'只有管理员才能删除"有人问"的问题', at_sender=False)
            return
        wild = union(context['group_id'], 1)
        a = ans.get(wild)
        if a:
            Question.delete().where(
                Question.quest == q,
                Question.rep_group == context['group_id'],
                Question.rep_member == 1,
            ).execute()
            del ans[wild]
            if not ans:
                del answers[q]
            await bot.send(context, f'我不再回答"{a}"了', at_sender=False)


@sv.on_command('查找QA', aliases=('查询问题', '查找问题', '看看QA', '看看qa', '看看问题'))
async def lookqa(session: CommandSession):
    uid = session.ctx['user_id']
    gid = session.ctx['group_id']
    result = Question.select(Question.quest).where(
        Question.rep_group == gid, Question.rep_member == uid)
    msg = ['您在该群中设置的问题是:']
    for res in result:
        msg.append(res.quest)
    await session.send('/'.join(msg), at_sender=True)


@sv.on_command('查看有人问', aliases=('看看有人问', '看看大家问', '查找有人问'))
async def lookgqa(session: CommandSession):
    gid = session.ctx['group_id']
    result = Question.select(Question.quest).where(
        Question.rep_group == gid, Question.rep_member == 1)
    msg = ['该群设置的"有人问"是:']
    for res in result:
        msg.append(res.quest)
    await session.send('/'.join(msg), at_sender=True)


@sv.on_message('group')
async def answer(bot, context):
    ans = answers.get(context['raw_message'])
    if ans:
        a = ans.get(union(context['group_id'], context['user_id']))
        if a:
            await bot.send(context, a, at_sender=False)
            return
        b = ans.get(union(context['group_id'], 1))
        if b:
            await bot.send(context, b, at_sender=False)
            return
