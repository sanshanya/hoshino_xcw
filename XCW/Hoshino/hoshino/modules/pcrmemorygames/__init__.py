# Refer to code of priconne game in HoshinoBot by @Ice-Cirno
# Under GPL-3.0 License

import os
import sqlite3


class Dao:
    def __init__(self, db_path):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._create_table()

    def connect(self):
        return sqlite3.connect(self.db_path)

    def _create_table(self):
        with self.connect() as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS score_record "
                "(gid INT NOT NULL, uid INT NOT NULL, score INT NOT NULL, PRIMARY KEY(gid, uid))"
            )

    def get_score(self, gid, uid):
        with self.connect() as conn:
            r = conn.execute(
                "SELECT score FROM score_record WHERE gid=? AND uid=?", (gid, uid)
            ).fetchone()
            return r[0] if r else 0

    def add_score_increment(self, gid, uid, score_increment):
        score = self.get_score(gid, uid)
        score += score_increment
        with self.connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO score_record (gid, uid, score) VALUES (?, ?, ?)",
                (gid, uid, score),
            )
        return score

    def get_ranking(self, gid):
        with self.connect() as conn:
            r = conn.execute(
                "SELECT uid, score FROM score_record WHERE gid=? ORDER BY score DESC LIMIT 10",
                (gid,),
            ).fetchall()
            return r


class GameMaster:
    def __init__(self, db_path):
        self.db_path = db_path
        self.playing = {}

    def is_playing(self, gid):
        return gid in self.playing

    def start_game(self, gid):
        return Game(gid, self)

    def get_game(self, gid):
        return self.playing[gid] if gid in self.playing else None

    @property
    def db(self):
        return Dao(self.db_path)


class Game:
    def __init__(self, gid, game_master):
        self.gid = gid
        self.gm = game_master
        self.answer = -1
        self.winner = []
        self.loser = []

    def __enter__(self):
        self.gm.playing[self.gid] = self
        return self

    def __exit__(self, type_, value, trace):
        del self.gm.playing[self.gid]

    def record_winner(self, uid):
        if uid not in self.winner:
            self.winner.append(uid)
        if uid in self.loser:
            self.loser.remove(uid)

    def record_loser(self, uid):
        if uid in self.winner:
            self.winner.remove(uid)
        if uid not in self.loser:
            self.loser.append(uid)

    def update_score(self):
        for i, uid in enumerate(self.winner):
            self.gm.db.add_score_increment(self.gid, uid, 2 if i==0 else 1)
        for uid in self.loser:
            self.gm.db.add_score_increment(self.gid, uid, -1)

    def get_first_winner_score(self):
        return self.gm.db.get_score(self.gid, self.winner[0]) if self.winner else -999