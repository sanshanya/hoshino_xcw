import sqlite3
import os

DB_PATH = os.path.expanduser('~/.hoshino/box_collection.db')

class BoxColleDao:
    def __init__(self):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        self._create_table()


    def _connect(self):
        return sqlite3.connect(DB_PATH)


    def _create_table(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS BOXCOLLETABLE
                          (UID            INT     NOT NULL,
                           DBNAME         TEXT    NOT NULL,
                           CHARAID        INT     NOT NULL,
                           CHARANAME      TEXT    NOT NULL,
                           STAR           TEXT    NOT NULL,
                           PRIMARY KEY(UID, DBNAME, CHARAID));''')
        except:
            raise Exception('创建box统计表发生错误')
 
           
    def _update_or_insert(self, user_id, db_name, chara_id, chara_name, star):
        try:
            conn = self._connect()
            conn.execute("INSERT OR REPLACE INTO BOXCOLLETABLE (UID,DBNAME,CHARAID,CHARANAME,STAR) \
                                VALUES (?,?,?,?,?)", (user_id, db_name, chara_id, chara_name, star))
            conn.commit()       
        except:
            raise Exception('更新box统计表发生错误')
            
    
    def _delete_by_user_id(self, user_id, db_name):
        try:
            conn = self._connect()
            conn.execute("DELETE FROM BOXCOLLETABLE WHERE UID=? AND DBNAME=?", (user_id, db_name))
            conn.commit()
        except:
            raise Exception('删除box统计表发生错误')
         
            
    def _delete_by_chara_id(self, chara_id, db_name):
        try:
            conn = self._connect()
            conn.execute("DELETE FROM BOXCOLLETABLE WHERE CHARAID=? AND DBNAME=?", (chara_id, db_name))
            conn.commit()
        except:
            raise Exception('删除box统计表发生错误')


    def _find_chara_id_by_user_id(self, user_id, db_name):
        try:
            r = self._connect().execute("SELECT CHARAID,STAR FROM BOXCOLLETABLE WHERE UID=? AND DBNAME=?",(user_id, db_name)).fetchall()
            return [] if r is None else {i[0]:i[1] for i in r}
        except:
            raise Exception('查找box统计表发生错误')
            

    def _find_by_user_id(self, user_id, db_name):
        try:
            r = self._connect().execute("SELECT CHARANAME,STAR FROM BOXCOLLETABLE WHERE UID=? AND DBNAME=?",(user_id, db_name)).fetchall()        
            return [] if r is None else {i[0]:i[1] for i in r}
        except:
            raise Exception('查找box统计表发生错误')

    
    def _find_by_chara_id(self, chara_id, db_name):
        try:
            r = self._connect().execute("SELECT UID,STAR FROM BOXCOLLETABLE WHERE CHARAID=? AND DBNAME=?",(chara_id, db_name)).fetchall()        
            return [] if r is None else {i[0]:i[1] for i in r}
        except:
            raise Exception('查找box统计表发生错误')


    def _find_by_primary_key(self, user_id, db_name, chara_id):
        try:
            r = self._connect().execute("SELECT STAR FROM BOXCOLLETABLE WHERE UID=? AND DBNAME=? AND CHARAID=?",(user_id, db_name, chara_id)).fetchone()
            return '' if r is None else r[0]
        except:
            raise Exception('查找box统计表发生错误')


    def _get_recorded_uid_list(self, db_name):
        try:
            recorded_uid_list = []
            r = self._connect().execute("SELECT UID FROM BOXCOLLETABLE WHERE DBNAME=?",(db_name,)).fetchall()
            for u in r:
                if u[0] not in recorded_uid_list:
                    recorded_uid_list.append(u[0])
            return recorded_uid_list
        except:
            raise Exception('查找box统计表发生错误')

 
    def _get_recorded_dbname_list(self):
        try:
            recorded_dbname_list = []
            r = self._connect().execute("SELECT DBNAME FROM BOXCOLLETABLE").fetchall()  
            for n in r:
                if n[0] not in recorded_dbname_list:
                    recorded_dbname_list.append(n[0])
            return recorded_dbname_list
        except:
            raise Exception('查找box统计表发生错误')
    
    
    def _get_recorded_charaname_list(self, db_name):
        try:
            recorded_charaid_list = []
            recorded_charaname_list = []
            r = self._connect().execute("SELECT CHARAID,CHARANAME FROM BOXCOLLETABLE WHERE DBNAME=?",(db_name,)).fetchall()
            for i in r:
                if i[0] not in recorded_charaid_list:
                    recorded_charaid_list.append(i[0])
                    recorded_charaname_list.append(i[1])
            return recorded_charaname_list
        except:
            raise Exception('查找box统计表发生错误')