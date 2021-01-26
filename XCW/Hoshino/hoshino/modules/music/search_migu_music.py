from hoshino import logger, aiorequests

USER_AGENT = "Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1"


async def search(keyword, result_num: int = 3):
    """ 搜索音乐 """
    song_list = []
    # ?rows=20&type=2&keyword=稻香&pgc=1

    headers = {
        "referer": "https://m.music.migu.cn/v3",
        "User-Agent": USER_AGENT
    }
    try:
        resp = await aiorequests.get(
            url=f"https://m.music.migu.cn/migu/remoting/scr_search_tag?rows=20&type=2&keyword={keyword}&pgc=1",
            headers=headers,
            timeout=3
        )
        res_data = await resp.json()
    except Exception as e:
        logger.warning(f'Request Migu Music Timeout {e}')
        return None
    try:
        for item in res_data['musics'][:result_num]:
            song_list.append(
                {
                    'url': 'https://music.migu.cn/v3/music/song/' + item['copyrightId'],
                    'purl': item['mp3'],
                    'image': item['cover'],
                    'title': item['songName'],
                    'content': item['singerName'],
                    'name': item['songName'],
                    'artists': item['singerName'],
                    'type': 'custom',
                    'subtype': 'migu'
                }
            )
        return song_list
    except KeyError as e:
        logger.warning(f'No Results: {e}')
        return None
