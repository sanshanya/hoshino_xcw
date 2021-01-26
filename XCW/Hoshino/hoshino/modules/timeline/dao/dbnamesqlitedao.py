import sqlite3
import os

DB_PATH = os.path.expanduser('~/.hoshino/timeline_database_name.db')

class TLDBNameDao:
    def __init__(self, group_id):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        self._create_table()
        if self._connect().execute("SELECT * FROM TLDBNAMETABLE WHERE GID=?",(group_id,)).fetchone()==None:
            self._insert(group_id, group_id)


    def _connect(self):
        return sqlite3.connect(DB_PATH)


    def _create_table(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS TLDBNAMETABLE
                          (GID INT PRIMARY KEY    NOT NULL,
                           TLDBNAME       TEXT    NOT NULL);''')
        except:
            raise Exception('创建轴库名表发生错误')

    
    def _insert(self, group_id, tldb_name):
        try:
            conn = self._connect()
            conn.execute("INSERT INTO TLDBNAMETABLE (GID,TLDBNAME) \
                                VALUES (?, ?)", (group_id, tldb_name))
            conn.commit()
        except (sqlite3.DatabaseError):
            raise Exception('添加轴库名表发生错误') 
 
           
    def _update_by_id(self, group_id, tldb_name):
        try:
            conn = self._connect()
            r = conn.execute("SELECT * FROM TLDBNAMETABLE WHERE GID=?",(group_id,)).fetchone()
            if r!=None:
                conn.execute("UPDATE TLDBNAMETABLE SET TLDBNAME=? WHERE GID=?",(tldb_name, group_id))
                conn.commit()
            else:
                raise Exception('更新轴库名表发生错误')
        except:
            raise Exception('更新轴库名表发生错误')


    def _find_by_id(self, group_id):
        try:
            r = self._connect().execute("SELECT TLDBNAME FROM TLDBNAMETABLE WHERE GID=?",(group_id,)).fetchone()        
            return r[0]
        except:
            raise Exception('查找轴发生错误')