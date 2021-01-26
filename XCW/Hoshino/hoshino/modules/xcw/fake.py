from hoshino import R, Service, priv, util
import json

sv_help = '''
- [造假@某人 名字说XXX]就会生成一条聊天记录
※后面持续跟@某人 名字说XXX可生成多条
'''.strip()

sv = Service(
    name = '造假',  #功能名
    use_priv = priv.NORMAL, #使用权限   
    manage_priv = priv.ADMIN, #管理权限
    visible = True, #是否可见
    enable_on_default = True, #是否默认启用
    bundle = '通用', #属于哪一类
    help_ = sv_help #帮助文本
    )

@sv.on_fullmatch(["帮助造假"])
async def bangzhu(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)
    

@sv.on_prefix("造假",only_to_me=False)
async def chat_say(bot, ev):
    print(ev)
    message = ev["message"]
    senderqq = []
    content = []
    tmp = ""
    data_all = []
    for msg_group in message:
        print(msg_group["type"])
        if msg_group["type"] == "at" :
            senderqq.append(msg_group["data"]["qq"])
            content.append(tmp)
            tmp = ""
        else :
            tmp = tmp + str(msg_group)
    content.append(tmp)

        
    for i in range(len(senderqq)):
        msg = content[i+1]
        sender,text = msg.split("说",2)
        data ={
        "type": "node",
        "data": {
            "name": sender,
            "uin": senderqq[i],
            "content": text
                }
                    }
        data_all.append(data)
    

    await bot.send_group_forward_msg(group_id=ev['group_id'], messages=data_all)