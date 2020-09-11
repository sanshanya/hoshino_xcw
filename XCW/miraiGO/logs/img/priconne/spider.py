import os
import re
import time
import json
import requests
from urllib.parse import urlparse, urlunparse
from requests.compat import quote, urljoin
from PIL import Image
from io import BytesIO

class Spider(object):

    def download_img(self, save_path, link):
        print('download_img from ', link, end=' ')
        resp = requests.get(link, stream=True)
        print('status_code=', resp.status_code, end=' ')
        if 200 == resp.status_code:
            if re.search(r'image', resp.headers['content-type'], re.I):
                print(f'is image, saving to {save_path}', end=' ')
                img = Image.open(BytesIO(resp.content))
                img.save(save_path)
                print('ok', end=' ')


    def download_icon_unit(self, start=1001, end=1200, star=3):
        base = 'https://redive.estertion.win/icon/unit/'
        save_dir = './unit/'
        os.makedirs(save_dir, exist_ok=True)

        def get_pic_name(pic_id, pre, end):
            return f'{pre}{pic_id:0>4d}{end}'


        for i in range(start, end):
            src_n = get_pic_name(i, '', f'{star}1.webp')
            dst_n = get_pic_name(i, 'icon_unit_', f'{star}1.png')
            self.download_img(os.path.join(save_dir, dst_n), urljoin(base, src_n))
            time.sleep(0.5)
            print('\n', end='')


    def download_comic(self, start=1, end=200, only_index=False):
        base = 'https://comic.priconne-redive.jp/api/detail/'
        save_dir = './comic/'
        os.makedirs(save_dir, exist_ok=True)

        def get_pic_name(id_):
            pre = 'episode_'
            end = '.png'
            return f'{pre}{id_}{end}'

        index = {}

        for i in range(start, end):
            print('getting comic', i, '...', end=' ')
            url = base + str(i)
            print('url=', url, end=' ')
            resp = requests.get(url)
            print('status_code=', resp.status_code)
            if 200 != resp.status_code:
                continue
            data = resp.json()[0]

            # if data['current_index'] != False:
            episode = data['episode_num']
            title = data['title']
            link = data['cartoon']
            index[episode] = {'title': title, 'link': link}
            print(index[episode])
            if not only_index:
                self.download_img(os.path.join(save_dir, get_pic_name(episode)), link)
            time.sleep(0.1)
            print('\n', end='')
            # else:
            #     print('current_index not True, ignore')

        with open(os.path.join(save_dir, 'index.json'), 'w', encoding='utf8') as f:
            json.dump(index, f, ensure_ascii=False)


if __name__ == '__main__':
    spider = Spider()
    # 运行过程出现404和200属正常情况
    spider.download_icon_unit(start=1130, end=1140, star=3)
    spider.download_icon_unit(start=1130, end=1140, star=1)
    spider.download_icon_unit(start=1030, end=1040, star=6)
    spider.download_icon_unit(start=1804, end=1809, star=3)
    # 如果需要爬取漫画，取消掉下面的这行注释
   # spider.download_comic(start=1, end=200, only_index=False)
