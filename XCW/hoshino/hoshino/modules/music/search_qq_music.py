from hoshino import logger, aiorequests

USER_AGENT = "Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1"


async def search(keyword, result_num: int = 3):
    """ 搜索音乐 """
    number = 5
    song_list = []
    params = {"w": keyword, "format": "json", "p": 0, "n": number}

    headers = {
        "referer": "http://m.y.qq.com",
        "User-Agent": USER_AGENT
    }
    try:
        resp = await aiorequests.get(
            url="http://c.y.qq.com/soso/fcgi-bin/search_for_qq_cp",
            params=params,
            headers=headers,
            timeout=3
        )
        res_data = await resp.json()
    except Exception as e:
        logger.warning(f'Request QQ Music Timeout {e}')
        return None
    try:
        for item in res_data['data']['song']['list'][:result_num]:
            song_list.append(
                {
                    'name': item['songname'],
                    'id': item['songid'],
                    'artists': ' '.join(
                        artist['name'] for artist in item['singer']
                    ),
                    'type': 'qq'
                }
            )
        return song_list
    except KeyError as e:
        logger.warning(f'No Result: {e}')
        return None
