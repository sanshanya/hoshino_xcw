import os,sys
import json
import random
from hoshino import util


class Run_chara:
    # 通过传入文件名 读入对应的角色Json文档进行初始化
    def __init__(self, id:str):
        project_path = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(project_path,'config.json')
        
        # 读文件
        with open(file_path,"r", encoding='UTF-8') as f:
            self.config = json.loads(f.read())
            

        # 搬运数据
        self.id = id
        self.name = self.config[id]['name']
        self.icon = self.config[id]["icon"]
        self.speed = self.config[id]['speed']
        self.skill = self.config[id]['skill']
        del self.config
        
   
        
    def getskill(self,sid):
        skill = self.skill[str(sid)]
        return skill
    def geticon(self):
        icon = self.icon
        return str(icon)
    def getname(self):
        name = self.name
        return str(name)   
    def getspeed(self):
        return self.speed
    def getskill_prob_list(self):
        prob_list = [0 for x in range(0,5)]
        sum = 1
        for i in range(1,5):
            prob_list[i]=self.skill[str(i)]["skill_porb"]
            sum -= prob_list[i]
        prob_list[0] = sum    
        return  prob_list   
    
            
            
        
