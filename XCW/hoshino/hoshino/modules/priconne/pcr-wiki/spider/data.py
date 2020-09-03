import peewee as pw

db = pw.SqliteDatabase('C:\\Users\cwx_x\Documents\workSpace\python\pcr_wiki\wiki\data.db')#填写你要更新的data.db的路径

class Info(pw.Model):
    id = pw.IntegerField()
    name = pw.TextField()
    guild = pw.TextField()
    birthday = pw.TextField()
    age = pw.TextField()
    height = pw.TextField()
    weight = pw.TextField()
    blood_type = pw.TextField()
    race = pw.TextField()
    hobby = pw.TextField()
    cv = pw.TextField()
    introduce = pw.TextField()
    start = pw.TextField()
    loop = pw.TextField()
    class Meta:
        database = db
        table_name = 'info'

class Skill(pw.Model):
    id = pw.IntegerField()
    name = pw.TextField()
    type = pw.TextField()
    description = pw.TextField()
    num = pw.TextField()
    effect = pw.TextField()
    class Meta:
        database = db
        table_name = 'skill'

class Kizuna(pw.Model):
    id = pw.IntegerField()
    name = pw.TextField()
    episode = pw.TextField()
    effect = pw.TextField()
    class Meta:
        database = db
        table_name = 'kizuna'

class Uniquei(pw.Model):
    id = pw.IntegerField()
    name = pw.TextField()
    num = pw.TextField()
    description = pw.TextField()
    class Meta:
        database = db
        table_name = 'uniquei'

class Props(pw.Model):
    id = pw.IntegerField()
    property = pw.TextField()
    base_value = pw.TextField()
    max_value = pw.TextField()
    class Meta:
        database = db
        table_name = 'props'