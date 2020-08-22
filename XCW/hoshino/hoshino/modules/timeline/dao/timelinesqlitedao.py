import sqlite3
import os

class TLSqliteDao:
    def __init__(self, dbname):
        self.db_path = os.path.expanduser('~/.hoshino/' + dbname + '.db')
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._create_table()
        
        
    def _connect(self):
        return sqlite3.connect(self.db_path)
    
    
    def _create_table(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS TLTABLE
                          (ID INTEGER PRIMARY KEY AUTOINCREMENT,
                           BOSSNAME       TEXT    NOT NULL,
                           DAMAGE         TEXT    NOT NULL, 
                           TIMELINE       TEXT    NOT NULL,
                           INTRODUCTION   TEXT    NOT NULL,
                           USERID         INT     NOT NULL,
                           APPROVAL       INT     NOT NULL);''')
        except:
            raise Exception('创建轴发生错误')
        
        
    def _insert(self, bossname, damage, introduction, timeline, userid=-1):
        try:
            conn = self._connect()
            conn.execute("INSERT INTO TLTABLE (ID,BOSSNAME,DAMAGE,TIMELINE,INTRODUCTION,USERID,APPROVAL) \
                                VALUES (NULL, ?, ?, ?, ?, ?, ?)", (bossname, damage, timeline, introduction, userid, 0))
            conn.commit()
        except (sqlite3.DatabaseError):
            raise Exception('添加轴发生错误')            
            
        
    def _add_approval(self, tid, approval):
        try:
            conn = self._connect()
            r = conn.execute("SELECT APPROVAL FROM TLTABLE WHERE ID=?",(tid,)).fetchone()
            a = r[0]
            conn.execute("UPDATE TLTABLE SET APPROVAL=? WHERE ID=?",(a+approval,tid))
            conn.commit()
        except:
            raise Exception('赞同轴发生错误')
        
        
    def _del_by_id(self, tid, userid):
        try:
            conn = self._connect()
            r = conn.execute("SELECT USERID FROM TLTABLE WHERE ID=?",(tid,)).fetchone()
            if userid!=r[0] and userid!=999:
                return False
            else:
                conn.execute("DELETE FROM TLTABLE WHERE ID=?;",(tid,))
                conn.commit()
                return True
        except:
            raise Exception('删除轴发生错误')


    def _update_by_id(self, tid, damage, introduction, timeline, userid):
        try:
            conn = self._connect()
            r = conn.execute("SELECT USERID FROM TLTABLE WHERE ID=?",(tid,)).fetchone()
            if userid!=r[0] and userid!=999:
                return False
            else:
                conn.execute("UPDATE TLTABLE SET DAMAGE=?, INTRODUCTION=?, TIMELINE=? WHERE ID=?;",(damage, introduction, timeline, tid))
                conn.commit()
                return True
        except:
            raise Exception('更新轴发生错误')


    def _find_by_id(self, tid):
        try:
            r = self._connect().execute("SELECT BOSSNAME,DAMAGE,TIMELINE,INTRODUCTION FROM TLTABLE WHERE ID=?",(tid,)).fetchone()        
            return r
        except:
            raise Exception('查找轴发生错误')

    
    def _find_by_bossname(self, bossname):
        try:
            r = self._connect().execute("SELECT ID,BOSSNAME,DAMAGE,INTRODUCTION,APPROVAL FROM TLTABLE WHERE BOSSNAME LIKE '%s%%' ORDER BY APPROVAL DESC"%bossname).fetchall()
            return self._2dtuple_to_1dlist(r)
        except:
            raise Exception('查找轴发生错误')
        

    def _find_all(self):
        try:
            r = self._connect().execute("SELECT ID,BOSSNAME,DAMAGE,INTRODUCTION,APPROVAL FROM TLTABLE ORDER BY APPROVAL DESC").fetchall()
            return self._2dtuple_to_1dlist(r)
        except:
            raise Exception('查找轴发生错误')
    
    
    @staticmethod
    def _2dtuple_to_1dlist(r):
        a = []
        for i in range(len(r)):
            b = []
            for j in range(len(r[i])):
                if j==0:
                    b.append('T'+'{0:02d}'.format(r[i][j]))
                elif j==len(r[i])-1:
                    b.append(str(r[i][j])+'赞')
                else:
                    b.append(str(r[i][j]))
            a.append('|'.join(b))
        return a
