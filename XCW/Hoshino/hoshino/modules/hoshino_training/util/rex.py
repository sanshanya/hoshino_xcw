import hoshino

def rex_replace(rex_pattern, func):
    rex = hoshino.trigger.rex
    for k in list(rex.allrex.keys()):
        if rex_pattern in k.pattern:
            rex.allrex[k].func = func
            return True
    return False
