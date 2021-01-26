import sqlite3
import os

DB_PATH = os.path.expanduser('~/.hoshino/box_collection_request.db')

class ColleRequestDao:
    def __init__(self):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        self._create_table()


    def _connect(self):
        return sqlite3.connect(DB_PATH)


    def _create_table(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS COLLEREQUESTTABLE
                          (UID             INT    NOT NULL,
                           GID             INT    NOT NULL,
                           DBNAME         TEXT    NOT NULL,
                           DETAIL         TEXT    NOT NULL,
                           COLLESETTING   TEXT    NOT NULL,
                           PRIMARY KEY (UID,GID));''')
        except:
            raise Exception('创建统计请求表发生错误')
 
           
    def _update_or_insert_by_id(self, user_id, group_id, db_name, detail, colle_setting):
        try:
            conn = self._connect()
            conn.execute("INSERT OR REPLACE INTO COLLEREQUESTTABLE (UID,GID,DBNAME,DETAIL,COLLESETTING) \
                          VALUES (?,?,?,?,?)", (user_id, group_id, db_name, detail, colle_setting))
            conn.commit()
        except:
            raise Exception('更新统计请求表发生错误')


    def _find_by_id(self, user_id):
        try:
            r = self._connect().execute("SELECT DBNAME,DETAIL,COLLESETTING,GID FROM COLLEREQUESTTABLE WHERE UID=?",(user_id,)).fetchone()        
            return r
        except:
            raise Exception('查找统计请求表发生错误')