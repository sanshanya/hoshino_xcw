import os
import sqlite3
from collections import Counter
from datetime import datetime, timedelta

from hoshino.util import DailyNumberLimiter


class CardRecordDAO:
    def __init__(self, db_path):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._create_table()

    def connect(self):
        return sqlite3.connect(self.db_path)

    def _create_table(self):
        with self.connect() as conn:
            # group_id, user_id, card_id
            conn.execute(
                "CREATE TABLE IF NOT EXISTS card_record"
                "(gid INT NOT NULL, uid INT NOT NULL, cid INT NOT NULL, num INT NOT NULL, PRIMARY KEY(gid, uid, cid))"
            )
            conn.execute(
                "CREATE TABLE IF NOT EXISTS limiter"
                "(key TEXT NOT NULL, num INT NOT NULL, date INT, PRIMARY KEY(key))"
            )

    def get_card_num(self, gid, uid, cid):
        with self.connect() as conn:
            r = conn.execute(
                "SELECT num FROM card_record WHERE gid=? AND uid=? AND cid=?", (gid, uid, cid)
            ).fetchone()
            return r[0] if r else 0

    def add_card_num(self, gid, uid, cid, increment=1):
        num = self.get_card_num(gid, uid, cid)
        num += increment
        with self.connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO card_record (gid, uid, cid, num) VALUES (?, ?, ?, ?)",
                (gid, uid, cid, num),
            )
        return num

    def get_cards_num(self, gid, uid):
        with self.connect() as conn:
            r = conn.execute(
                "SELECT cid, num FROM card_record WHERE gid=? AND uid=? AND num>0", (gid, uid)
            ).fetchall()
        return {c[0]: c[1] for c in r} if r else {}

    def get_surplus_cards(self, gid, uid):
        with self.connect() as conn:
            r = conn.execute(
                "SELECT cid, num FROM card_record WHERE gid=? AND uid=? AND num>1", (gid, uid)
            ).fetchall()
        return {c[0]: (c[1]-1) for c in r} if r else {}

    def get_group_ranking(self, gid, uid):
        with self.connect() as conn:
            r = conn.execute(
                "SELECT uid FROM card_record WHERE gid=? AND num>0", (gid,)
            ).fetchall()
        if not r:
            return -1
        cards_num = Counter([s[0] for s in r])
        if uid not in cards_num:
            return -1
        user_card_num = cards_num[uid]
        return sum(n > user_card_num for n in cards_num.values()) + 1

    def exist_check(self,key):
        try:
            key = str(key)
            with self.connect() as conn:
                conn.execute("INSERT INTO limiter (key,num,date) VALUES (?, 0,-1)",(key,),)
            return
        except:
            return

    def get_num(self,key):
        self.exist_check(key)
        key = str(key)
        with self.connect() as conn:
            r = conn.execute(
                "SELECT num FROM limiter WHERE key=? ", (key,)
            ).fetchall()
            r2 = r[0]
        return r2[0]

    def clear_key(self,key):
        key = str(key)
        self.exist_check(key)
        with self.connect() as conn:
            conn.execute("UPDATE limiter SET num=0 WHERE key=?",(key,),)
        return
    
    def increment_key(self,key,num):
        self.exist_check(key)
        key = str(key)
        with self.connect() as conn:
            conn.execute("UPDATE limiter SET num=num+? WHERE key=?",(num,key,))
        return

    def get_date(self,key):
        self.exist_check(key)
        key = str(key)
        with self.connect() as conn:
            r = conn.execute(
                "SELECT date FROM limiter WHERE key=? ", (key,)
            ).fetchall()
            r2 = r[0]
        return r2[0]

    def set_date(self,date,key):
        print(date)
        self.exist_check(key)
        key = str(key)
        with self.connect() as conn:
            conn.execute("UPDATE limiter SET date=? WHERE key=?",(date,key,),)
        return

class ExchangeRequest:
    def __init__(self, sender_uid, card1_id, card1_name, target_uid, card2_id, card2_name):
        self.sender_uid = sender_uid
        self.card1_id = card1_id
        self.card1_name = card1_name
        self.target_uid = target_uid
        self.card2_id = card2_id
        self.card2_name = card2_name
        self.request_time = datetime.now()


class ExchangeRequestMaster:
    def __init__(self, max_valid_time):
        self.last_exchange_request = {}
        self.max_valid_time = max_valid_time

    def add_exchange_request(self, gid, uid, request: ExchangeRequest):
        self.last_exchange_request[(gid, uid)] = request

    def get_last_exchange_request_time(self, gid, uid):
        return self.last_exchange_request[(gid, uid)].request_time if (gid, uid) in self.last_exchange_request else datetime(2020, 4, 17, 0, 0, 0, 0)

    def has_exchange_request_to_confirm(self, gid, uid):
        now_time = datetime.now()
        delta_time = now_time - self.get_last_exchange_request_time(gid, uid)
        return delta_time.total_seconds() <= self.max_valid_time

    def get_exchange_request(self, gid, uid) -> ExchangeRequest:
        return self.last_exchange_request[(gid, uid)]

    def delete_exchange_request(self, gid, uid):
        if (gid, uid) in self.last_exchange_request:
            del self.last_exchange_request[(gid, uid)]

DB_PATH = os.path.expanduser("~/.hoshino/poke_man_pcr.db")
db = CardRecordDAO(DB_PATH)

class DailyAmountLimiter(DailyNumberLimiter):
    def __init__(self, types, max_num, reset_hour):
        super().__init__(max_num)
        self.reset_hour = reset_hour
        self.type=types

    def check(self, key) -> bool:
        now = datetime.now(self.tz)
        key = list(key)
        key.append(self.type)
        key = tuple(key)
        day = (now - timedelta(hours=self.reset_hour)).day
        if day != db.get_date(key):
            db.set_date(day,key)
            db.clear_key(key)
        return bool(db.get_num(key) < self.max)

    def get_num(self, key):
        key = list(key)
        key.append(self.type)
        key = tuple(key)
        return db.get_num(key)

    def increase(self, key, num=1):
        key = list(key)
        key.append(self.type)
        key = tuple(key)
        db.increment_key(key,num)

    def reset(self, key):
        key = list(key)
        key.append(self.type)
        key = tuple(key)
        db.clear_key(key)
