import datetime
import aiohttp

from arrow.arrow import Arrow
from hoshino import log
try:
    import ujson as json
except:
    import json

logger = log.new_logger('calendar')

_calendar_url = {
    "jp": "https://tools.yobot.win/calender/#jp",
    "tw": "https://pcredivewiki.tw/",
    "cn": "https://mahomaho-insight.info/",
}

_calendar_json_url = {
    "jp": "http://toolscdn.yobot.win/calender/jp.json",
    "tw": "https://pcredivewiki.tw/static/data/event.json",
    "cn": "https://mahomaho-insight.info/cached/gameevents.json",
}

class Event:
    def __init__(self, glo_setting: dict, *args, **kwargs):
        self.setting = glo_setting
        self.timezone = datetime.timezone(datetime.timedelta(hours=0))
        self.timeline = None

    async def load_timeline_async(self, rg=None):
        if rg is None:
            rg = self.setting.get("calendar_region", "cn")
        if rg == "jp":
            timeline = await self.load_timeline_jp_async()
            if timeline is None:
                return
            self.timeline = timeline
            logger.info("刷新日服日程表成功")
        elif rg == "tw":
            timeline = await self.load_timeline_tw_async()
            if timeline is None:
                return
            self.timeline = timeline
            logger.info("刷新台服日程表成功")
        elif rg == "cn":
            timeline = await self.load_timeline_cn_async()
            if timeline is None:
                return
            self.timeline = timeline
            logger.info("刷新国服日程表成功")

    def load_time_jp(self, timestr) -> Arrow:
        d_time = datetime.datetime.strptime(timestr, r"%Y/%m/%d %H:%M:%S")
        a_time = Arrow.fromdatetime(d_time)
        if a_time.time() < datetime.time(hour=4):
            a_time -= datetime.timedelta(hours=4)
        return a_time

    async def load_timeline_jp_async(self):
        event_source = _calendar_json_url.get(self.setting["calendar_region"])
        async with aiohttp.request("GET", url=event_source) as response:
            if response.status != 200:
                print('error')
            res = await response.text()
        events = json.loads(res)
        timeline = Event_timeline()
        for e in events:
            timeline.add_event(
                self.load_time_jp(e["start_time"]),
                self.load_time_jp(e["end_time"]),
                e["name"],
            )
        return timeline

    def load_time_tw(self, timestr) -> Arrow:
        d_time = datetime.datetime.strptime(timestr, r"%Y/%m/%d %H:%M")
        a_time = Arrow.fromdatetime(d_time)
        if a_time.time() < datetime.time(hour=5):
            a_time -= datetime.timedelta(hours=5)
        return a_time

    async def load_timeline_tw_async(self):
        event_source = _calendar_json_url.get(self.setting["calendar_region"])
        async with aiohttp.request("GET", url=event_source) as response:
            if response.status != 200:
                print('error')
            res = await response.text()
        events = json.loads(res)
        timeline = Event_timeline()
        for e in events:
            timeline.add_event(
                self.load_time_tw(e["start_time"]),
                self.load_time_tw(e["end_time"]),
                e["campaign_name"],
            )
        return timeline

    def load_time_cn(self, timestr) -> Arrow:
        d_time = datetime.datetime.strptime(timestr, r"%Y/%m/%d %H:%M")
        a_time = Arrow.fromdatetime(d_time)
        if a_time.time() < datetime.time(hour=5):
            a_time -= datetime.timedelta(hours=5)
        return a_time

    async def load_timeline_cn_async(self):
        event_source = _calendar_json_url.get(self.setting["calendar_region"])
        async with aiohttp.request("GET", url=event_source) as response:
            if response.status != 200:
                print('error')
            res = await response.text()
        events = json.loads(res)
        timeline = Event_timeline()
        for e in events["cn"]:
            if "desc" not in e.keys():
                timeline.add_event(
                    self.load_time_cn(e["start"]),
                    self.load_time_cn(e["end"]),
                    e["title"],
                )
        return timeline

    def get_day_events(self, match_num) -> tuple:
        if match_num == 2:
            daystr = "今天"
            date = Arrow.now(tzinfo=self.timezone)
        elif match_num == 3:
            daystr = "明天"
            date = Arrow.now(tzinfo=self.timezone) + datetime.timedelta(days=1)
        elif match_num & 0xf00000 == 0x100000:
            year = (match_num & 0xff000) >> 12
            month = (match_num & 0xf00) >> 8
            day = match_num & 0xff
            daystr = "{}年{}月{}日".format(2000+year, month, day)
            try:
                date = Arrow(2000+year, month, day)
            except ValueError as v:
                logger.error(f'日期错误{v}')
        events = self.timeline.at(date)
        return (daystr, events)

    async def get_week_events(self) -> str:
        try:
            await self.load_timeline_async()
        except Exception as e:
            logger.error("刷新日程表失败，失败原因："+str(e))
        reply = "一周日程："
        date = Arrow.now(tzinfo=self.timezone)
        for i in range(7):
            events = self.timeline.at(date)
            events_str = "\n⨠".join(events)
            if events_str == "":
                events_str = "没有记录"
            daystr = date.format("MM月DD日")
            reply += "\n======{}======\n⨠{}".format(daystr, events_str)
            date += datetime.timedelta(days=1)
        reply += "\n\n更多日程：{}".format(
            _calendar_url.get(self.setting["calendar_region"]))
        return reply

    async def send_daily_async(self, num=2):
        logger.info("正在刷新日程表")
        try:
            await self.load_timeline_async()
        except Exception as e:
            logger.error("刷新日程表失败，失败原因："+str(e))
        _, events = self.get_day_events(num)
        events_str = "\n".join(events)
        if events_str is None:
            return
        if num == 2:
            msg = "今日活动：\n{}".format(events_str)
        else:
            msg = "明日活动：\n{}".format(events_str)
        return msg
        
class Event_timeline:
    def __init__(self):
        self._tineline = dict()

    def add_event(self, start_t: Arrow, end_t: Arrow, name):
        t = start_t
        while t <= end_t:
            daystr = t.format(fmt="YYYYMMDD", locale="zh_cn")
            if daystr not in self._tineline:
                self._tineline[daystr] = list()
            self._tineline[daystr].append(name)
            t += datetime.timedelta(days=1)

    def at(self, day: Arrow):
        daystr = day.format(fmt="YYYYMMDD", locale="zh_cn")
        return self._tineline.get(daystr, ())