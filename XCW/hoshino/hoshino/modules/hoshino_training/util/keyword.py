import hoshino

def keyword_replace(keyword_list, func):
    keywords = set()
    for keyword in keyword_list:
        keyword = hoshino.util.normalize_str(keyword)
        keywords.add(keyword)
    rex = hoshino.trigger.keyword
    for k in list(rex.allkw.keys()):
        if k in keywords:
            rex.allkw[k].func = func

def keyword_remove(keyword_list):
    keywords = set()
    for keyword in keyword_list:
        keyword = hoshino.util.normalize_str(keyword)
        keywords.add(keyword)
    rex = hoshino.trigger.keyword
    for k in list(rex.allkw.keys()):
        if k in keywords:
            rex.allkw.pop(k)

def keyword_add(keyword_list, original_list):
    sf = keyword_get_servicefunc(original_list)
    if not sf:
        return False
    allkw = hoshino.trigger.keyword.allkw
    for keyword in keyword_list:
        keyword = hoshino.util.normalize_str(keyword)
        if keyword not in allkw:
            allkw[keyword] = sf

def keyword_get_servicefunc(keyword_list):
    keywords = set()
    for keyword in keyword_list:
        keyword = hoshino.util.normalize_str(keyword)
        keywords.add(keyword)
    rex = hoshino.trigger.keyword
    for k in list(rex.allkw.keys()):
        if k in keywords:
            return rex.allkw[k] #返回第一个找到的函数
    return None

def keyword_get_func(keyword_list):
    sf = keyword_get_servicefunc(keyword_list)
    if sf:
        return sf.func
    return None