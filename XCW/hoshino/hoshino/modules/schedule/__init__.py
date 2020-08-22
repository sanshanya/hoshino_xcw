from hoshino import Service
from urllib import request
import json
import datetime
import re

URL = 'https://static.biligame.com/pcr/gw/calendar.js'
header = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'

data = {
    'calendar_days': 7,  # 日程表返回包括今天在内多长时间的日程，默认是7天
    'Refresh_date': '',  # 上次爬取日程表的日期
    'schedule_data': ''  # 从官方日历爬取下来的数据
}

# day_key里保存的是每天的信息分类，"qdhd"是多倍掉落庆典，"tdz"是公会战，
# "tbhd"是公会之家家具上架，"jqhd"是活动地图，"jssr"是角色生日
# 你可以自定义这个列表，删掉不想看到的活动
day_key = ["qdhd", "tdz", "tbhd", "jqhd", "jssr"]


sv = Service('日程表')

@sv.on_fullmatch(('国服日程表','日程表'))
async def Schedule(bot, ev):
    # 调用的时候比对上次爬取日程表时间，不是今天就重新爬取日程表，是今天就直接返回

    if data['Refresh_date'] != str(datetime.date.today()):

        status = refresh_schedule()
        if not status[0]:
            await bot.send(ev, f'刷新日程表失败，错误代码{status[1]}')
            return
        data['Refresh_date'] = str(datetime.date.today())  # 爬取时间改为今天
        await bot.send(ev, return_schedule())
    else:
        await bot.send(ev, return_schedule())


@sv.on_fullmatch('刷新日程表')
async def re_Schedule(bot, ev):
    status = refresh_schedule()
    if status[0]:
        await bot.send(ev, '刷新日程表成功')
        data['Refresh_date'] = str(datetime.date.today())  # 爬取时间改为今天
    else:
        await bot.send(ev, f'刷新日程表失败，错误代码{status[1]}')


@sv.on_fullmatch(('今日活动','日程','今日日程'))
async def Schedule(bot, ev):

    if data['Refresh_date'] != str(datetime.date.today()):
        status = refresh_schedule()
        if not status[0]:
            await bot.send(ev, f'刷新日程表失败，错误代码{status[1]}')
            return
        data['Refresh_date'] = str(datetime.date.today())  # 爬取时间改为今天
        await bot.send(ev, return_schedule(1))
    else:
        await bot.send(ev, return_schedule(1))



def refresh_schedule():
    # 刷新日程表
    schedule = request.Request(URL)
    schedule.add_header('User-Agent', header)

    with request.urlopen(schedule) as f:
        if f.code != 200:#检查返回的状态码是否是200
            return [False, f.code]

        rew_data = f.read().decode('utf-8')#bytes类型转utf-8

        data['schedule_data'] = json.loads(rew_data[152:-35])#去掉头尾没用的数据保存到'schedule_data'
        return [True, "ok"]


def return_schedule(calendar_days=data['calendar_days']):
    # 返回日程表信息

    t = datetime.date.today()  # 要读取的日期
    year, month, day = str(t).split("-")  # 分割年月日

    activity_info_list = []
    info_list = []
    infos = ''

    for _ in range(calendar_days):
        for i in data['schedule_data']:
            if i['year'] == year and i['month'] == month:#官方数据每一个月份是一个列表，检查当前列表年月是否符合
                if day in i['day']: #检查是否有查询日期当天的数据
                    for key in day_key:
                        if i['day'][day][key] != '': #空的活动数据跳过

                            info_list.extend(re.findall("class='cl-t'>.+?</div>", i['day'][day][key]))#用正则截取活动信息

                if info_list:#如果列表不是空的
                    activity_info_list = [info[13:-6] for info in info_list]#去掉每条信息前后的正则匹配参数，只保留活动信息

                if not activity_info_list:#如果列表是空的
                    activity_info_list[0] = '没有活动信息'

                infos += '=======' + str(t).replace("-", "年", 1).replace("-", "月", 1) + '日' + '=======\n'
                for i in activity_info_list:
                    infos += '>>>' + i + '\n'

        t += datetime.timedelta(days=1)  # 改为下一天的日期
        year, month, day = str(t).split("-")  # 分割年月日
        
        activity_info_list = []
        info_list = []

    # 返回活动信息字符串
    return infos


