# 原神UID查询

---
插件调用的是米游社角色信息的接口,查询的信息也是基于上面的基础信息<br>
需要到米游社获取cookie配置到`config.yml`文件里

安装依赖
> pip install pyyaml -i https://pypi.tuna.tsinghua.edu.cn/simple
>
> pip install sqlitedict -i https://pypi.tuna.tsinghua.edu.cn/simple


文件夹丢到modules目录下 需要到bot的配置里的 MODULES_ON 添加 'genshinuid'

例如hoshinov2如下配置和路径

文件丢到 hoshino/modules/genshinuid

修改文件添加模块 `hoshino/config/__bot__.py`

```python
MODULES_ON = {
    'genshinuid',
}
```

---

命令  | 说明 | 例
------------- | ------------- | -------------
ys#UID  | 查询一个UID信息 | ys#105293904
ys#  | 查询用户上一次查询的UID信息 | ys#

# 鸣谢

[YuanShen_User_Info](https://github.com/Womsxd/YuanShen_User_Info)
