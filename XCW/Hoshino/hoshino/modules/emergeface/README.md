# 人脸合成(阴间功能)


> 首先要到  https://console.faceplusplus.com.cn/  注册<br>
> apikey   https://console.faceplusplus.com.cn/app/apikey/list  然后申请获得 API Key 和 API Secret <br>
> 开发文档  https://console.faceplusplus.com.cn/documents/20813963 <br>
---

拿到API Key 和 API Secret 后 编辑 `mergeface.py` 开头处填入

```python
params = {
    'api_key': '',  # 申请的 API Key 填这里
    'api_secret': '',  # 申请的 API Secret 填这里
    'merge_rate': 50,  # 融合比例，范围 [0,100]。数字越大融合结果包含越多融合图特征 默认值为50
    'feature_rate': 80  # 五官融合比例，范围 [0,100]。主要调节融合结果图中人像五官相对位置，数字越小融合图中人像五官相对更集中 。 默认值为45
}
```

放到插件目录下就好比如<br>
`hoshino/modules/groupmaster/mergeface.py`<br>


## 使用方法

群聊发送 换脸

然后发2张图就可