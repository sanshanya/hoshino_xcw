from hoshino import R, Service, priv, util
import json
sv = Service('fake', visible=False)
@sv.on_prefix("造假",only_to_me=True)
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