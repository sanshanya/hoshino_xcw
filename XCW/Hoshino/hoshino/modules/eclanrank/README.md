# pcr公会站排行插件

鸣谢数据来源 https://kengxxiao.github.io/Kyouka/

---

安装依赖
> pip install pyyaml -i https://pypi.tuna.tsinghua.edu.cn/simple
>
> pip install sqlitedict -i https://pypi.tuna.tsinghua.edu.cn/simple



文件夹丢到modules目录下
需要到bot的配置里的 MODULES_ON 添加 'eclanrank'

例如hoshinov2如下配置和路径

文件丢到 hoshino/modules/eclanrank

修改文件添加模块 `hoshino/config/__bot__.py`
```python
MODULES_ON = {
   'eclanrank',
}
```

---

命令  | 说明 | 例
------------- | ------------- | -------------
会战排行  | 查询公会名或排行 | 会战排行K.A. <br>会战排行1000
会战锁定  | 锁定后根据设定自动推送排行信息<br>并且会自动记录上次的排行信息做比较 | 会战锁定K.A.
会战解锁 | 解锁一个被锁定的公会 | 会战解锁K.A.
公会排行 | 查询当前锁定的公会 | 公会排行

## 配置文件
```yaml
# 管理员
admins:
  - 389897773

# 缓存存放目录
cache_dir: ./data/


# 触发的命令
comm:
  # 查询一个公会排行  可以是公会名字 可以是排名
  keyword: ["[会公工查][战会询][排查公][行名询会]"]

  # 锁定一个公会 可以直接使用会战排行查询或者每个设定的时间推送
  locked: ["[会公工][战会][锁绑]定"]
  # 解锁一个公会
  unlocked: ["[会公工][战会]解[锁除绑]"]
  #
  defaultLucked: ["[会公工][战会][排查][行名询]$"]

#规则
rules:
  # 是否只允许管理员锁定或解锁公会
  only_admin_can_locked: true

  # 是否每个群只能绑定一个公会
  only_one_locked: false



  # -------------------------------
  # 是否开启实时推送
  enable_clan_cron: false

  # 对锁定的公会多长时间更新广播一次 单位小时
  lock_clan_cron_time: 1

  # -------------------------------


  # -------------------------------
  # 定时任务
  enable_broadcast_time: true
  # 设置默认每天早上5点半推送一次
  broadcast_time:
    day_of_week: '*'
    hour: 5
    minute: 30
  # -------------------------------


  # -------------------------------
  # 获取数据的服务器地址
  base_url: https://service-kjcbcnmw-1254119946.gz.apigw.tencentcs.com
  # 获取数据的请求头
  headers:
    Content-Type: application/json
    Referer: https://kengxxiao.github.io/Kyouka/
    Custom-Source: erinilis
  # -------------------------------

str:
  # 自定义查询信息显示
  print_rank_info: |
    排名: {rank}  {rank_ext}
    公会: {clan_name}
    会长: {leader_name}
    UID: {leader_viewer_id}
    成员: {member_num}
    分数: {score}  {score_ext}
    进度: {process}

```
