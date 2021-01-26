# nga风纪区的黑名单


> 数据来源 
> [[风纪区] [国服]会战黑名单(正式运行中)](https://bbs.nga.cn/read.php?tid=22042044&_ff=-10308342&rand=294)
> [公主连结国服黑名单](https://docs.qq.com/sheet/DV1JqSHJ5aEVNUG1q)

---

由于数据是excel表格 只能通过固定的算法得到数据

只要表格的列数增加不修改代码后会造成无法使用

---
放到插件目录下就好比如 `hoshino/modules/eclanblack/`

修改文件添加模块 `hoshino/config/__bot__.py`
```python
MODULES_ON = {
   'eclanblack',
}
```

> 对应的hoshino服务是 clanblack

---

## 使用方法是

失信UID或者QQ号

例如根据UID搜索

失信`123456789789`

例如根据QQ搜索

失信`123456789`

---
>*每天0点都会刷新一下黑名单列表