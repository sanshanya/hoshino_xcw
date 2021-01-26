import re, time, os
from selenium.common.exceptions import NoSuchElementException
def get_chara_skill(driver, research=0):
    try:
        skill_boxes = driver.find_elements_by_class_name('skill-box')
        chara_skells = []
        for s_b in skill_boxes:
            skill = {}
            skill['skill_name'] = s_b.find_element_by_class_name('skill-name').text
            skill['skill_type'] = s_b.find_element_by_class_name('skill-type').text

            skill['description'] = s_b.find_element_by_class_name('skill-description').text
            skill['description'] = re.sub(r'(EX)?技能[1-3]?\+?|必殺技|\n','', skill['description'])
            skill['description'] = skill['description'].replace(skill['skill_name'], '')
            
            img_src = s_b.find_element_by_class_name('img-fluid').get_attribute('src')
            num_match = re.search(r'[0-9]+', os.path.basename(img_src))
            if num_match:
                skill['skill_num'] = num_match.group(0)
            else:
                skill['skill_num'] = -1

            skill['skill_effect'] = []
            skill_effects = s_b.find_elements_by_css_selector('.skill-effect > .mb-2')
            for s_e in skill_effects:
                s_e_divs = s_e.find_elements_by_tag_name('div')
                e_txt = ''
                for div in s_e_divs:
                    if div.text:
                        e_txt += div.text
                if e_txt:
                    e_txt = e_txt.replace('\n', '')
                    skill['skill_effect'].append(e_txt)
            chara_skells.append(skill)
        return chara_skells
    except NoSuchElementException as err :
        research += 1
        print(f'get_chara_skill_error ({research}) : {err}')
        time.sleep(1)
        if research < 4:
            get_chara_skill(driver, research )
        else:
            raise NoSuchElementException(err) 
         
def get_chara_info(driver, research=0):
    info = {}
    keys = {
        '名字': 'name',
        '公會': 'guild',
        '生日': 'birthday',
        '年齡': 'age',
        '身高': 'height',
        '體重': 'weight',
        '血型': 'blood_type',
        '種族': 'race',
        '喜好': 'hobby',
        '聲優': 'cv'
    }
    try:
        # 获得角色信息
        table = driver.find_element_by_class_name('chara-table')
        tr_list = table.find_elements_by_tag_name('tr')
        for tr in tr_list:
            item = tr.find_element_by_tag_name('th').text
            info[keys.get(item, item)] = tr.find_element_by_tag_name('td').text

        # 获取介绍
        intro = driver.find_elements_by_css_selector('.row>.col-lg-7>.d-block')
        if intro:
            info['introduce']= intro[0].text
            info['introduce'] = info['introduce'].replace('簡介\n', '')
        return info
    except NoSuchElementException as err:
        research += 1
        print(f'get_chara_info_error ({research}) : {err}')
        time.sleep(1)
        if research < 3:
            get_chara_info(driver, research)
        else:
            raise NoSuchElementException(err)

def get_chara_kizuna(driver):
    kizuna_tables = driver.find_elements_by_css_selector('.chara-table.mb-3')
    count = len(kizuna_tables)
    if count != 1: count = count / 3
    kizuna = {}
    for table in kizuna_tables:
        # 检查是否爬取到所有羁绊
        if len(kizuna) == count:
            break
        
        name = table.find_element_by_xpath('.//th[@colspan=2]').get_attribute('innerText')
        # 检查羁绊是否以及爬取过
        if name in kizuna or name == '':
            continue
        else:
            # 创建角色羁绊
            kizuna[name] = {}
       
        for tr in table.find_elements_by_tag_name('tr')[1:]:
            
            epi_key = tr.find_element_by_tag_name('th').get_attribute('innerText')
            effect = tr.find_element_by_tag_name('td').get_attribute('innerHTML')

            # html标签替换为分割符
            effect = re.sub(r'<div[^>]*>|</div>|<!-+>', '~', effect)
            # 利用贪婪匹配去除多余分割符
            effect = re.sub(r'~+', '~', effect)
            effect = effect.strip('~')
            kizuna[name][epi_key] = effect.split('~')
    return kizuna

def get_act_pattern(driver):
    act_pattern = {}
    for h4 in driver.find_elements_by_css_selector('h4.item-sub-title'):
        if h4.text == '起手':
            parent_node = h4.find_element_by_xpath('..')
            start_pattern = []
            for img in parent_node.find_elements_by_tag_name('img'):
                img_src = img.get_attribute('src')
                pt = os.path.splitext(os.path.basename(img_src))[0][-4:]
                start_pattern.append(pt)
            act_pattern['start'] = start_pattern

        if h4.text == '循環':
            parent_node = h4.find_element_by_xpath('..')
            loop_pattern = []
            for img in parent_node.find_elements_by_tag_name('img'):
                img_src = img.get_attribute('src')
                act = os.path.splitext(os.path.basename(img_src))[0][-4:]
                if act == 'tack':
                    act = 'attack'
                loop_pattern.append(act)
            act_pattern['loop'] = loop_pattern   

    return act_pattern

def get_unique_weapon(driver):
    for h3 in driver.find_elements_by_css_selector('h3.item-title.mb-0'):
        weapon = {}
        if '專用裝備' in h3.text:
            box = h3.find_element_by_xpath('..').find_element_by_class_name('prod-info-box')
            imgsrc = box.find_element_by_class_name('img-fluid').get_attribute('src')
            num_match = re.search(r'[0-9]+', os.path.basename(imgsrc))
            if num_match:
                weapon['weapon_num'] = num_match.group(0)
            else:
                weapon['weapon_num'] = -1

            weapon['name'] = box.find_element_by_id('0').text
            weapon['description'] = box.find_element_by_css_selector('.col-lg-8.col-12>p').text
            weapon['props'] = []
            for pop_box in box.find_elements_by_class_name('prod-data'):
                prop = {}
                prop['property'] = pop_box.find_element_by_class_name('title').text
                value = pop_box.find_element_by_class_name('prod-value').text
                value = value.replace(' ', '')
                value = value.replace(')', '')
                value_list = value.split('(')
                prop['base_value'] = value_list[0]
                prop['max_value'] = value_list[1]
                weapon['props'].append(prop)
            return weapon if weapon else False 

def fetch(driver):
    chara_data = {}
    chara_data['info'] = get_chara_info(driver)
    chara_data['kizuna'] = get_chara_kizuna(driver)
    chara_data['skill'] = get_chara_skill(driver)

    uniquei_weapon = get_unique_weapon(driver)
    if uniquei_weapon:
        # skills = chara_data['skill']
        # for index in range(len(skills)):
        #     if '專武強化技能' in skills[index]['skill_type']:
        #         uniquei_weapon['strengthen_skill'] = skills[index]
        #         # 删除技能中的专武强化技
        #         # skills.pop(index)
        #         break
        
        chara_data['uniquei'] = uniquei_weapon
    
    chara_data['pattern'] = get_act_pattern(driver)
    return chara_data