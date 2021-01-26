import sqlite3
import os

DB_PATH = os.path.expanduser('~/.hoshino/box_collection_setting.db')

class ColleSettingDao:
    def __init__(self):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        self._create_table()


    def _connect(self):
        return sqlite3.connect(DB_PATH)


    def _create_table(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS COLLESETTINGTABLE
                          (GID INT PRIMARY KEY    NOT NULL,
                           DBNAME         TEXT    NOT NULL,
                           BROADCASTLIST  TEXT    NOT NULL,
                           DETAIL         TEXT    NOT NULL,
                           COLLESETTING   TEXT    NOT NULL);''')
        except:
            raise Exception('创建统计设定表发生错误')


    def _update_or_insert_by_id(self, group_id, db_name, broadcast_list_str, detail, colle_setting):
        try:
            conn = self._connect()
            conn.execute("INSERT OR REPLACE INTO COLLESETTINGTABLE (GID,DBNAME,BROADCASTLIST,DETAIL,COLLESETTING) \
                                VALUES (?,?,?,?,?)", (group_id, db_name, broadcast_list_str, detail, colle_setting))
            conn.commit()
        except:
            raise Exception('更新统计设定表发生错误')


    def _find_by_id(self, group_id):
        try:
            r = self._connect().execute("SELECT DBNAME,BROADCASTLIST,DETAIL,COLLESETTING FROM COLLESETTINGTABLE WHERE GID=?",(group_id,)).fetchone()        
            return r
        except:
            raise Exception('查找统计设定表发生错误')