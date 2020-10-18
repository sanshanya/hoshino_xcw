import requests
import math
from functools import reduce
from urllib.parse import urlparse
from urllib import parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from pixivpy3 import *
from . import download, util

config = util.get_config()

pixiv_tran = util.get_json('pixiv_tran.json')


def img_proxy(url):
    return config.setting.proxy_img_service + 'https://i.pixiv.cat%s' % urlparse(url).path


def get_original_image(illust):
    if illust.get('meta_single_page') and illust.meta_single_page and illust.meta_single_page.original_image_url:
        return illust.meta_single_page.original_image_url
    else:
        return ''


def __proxy_illusts_img__(illusts):
    res = []

    def proxy_image_urls(image_urls):
        image_urls.large = img_proxy(image_urls.large)
        image_urls.medium = img_proxy(image_urls.medium)
        image_urls.square_medium = img_proxy(image_urls.square_medium)
        if image_urls.get('original'):
            image_urls.original = img_proxy(image_urls.original)
        return image_urls

    for item in illusts:
        item.image_urls = proxy_image_urls(item.image_urls)
        if item.get('meta_single_page') and item.meta_single_page and item.meta_single_page.original_image_url:
            item.meta_single_page.original_image_url = img_proxy(get_original_image(item))
        if item.get('meta_pages') and item.meta_pages:
            item.meta_pages = list(map(lambda x: {'image_urls': proxy_image_urls(x.image_urls)}, item.meta_pages))
        res.append(item)
    return res


def get_img_urls(illust):
    info = illust.image_urls
    info['original'] = get_original_image(illust)
    info['meta_pages'] = illust.meta_pages
    return util.dict_to_object(info)


def download_illust_image(illust, retry=3):
    img_urls = get_img_urls(illust)
    url = img_urls.medium
    illust['local_img'] = ''
    try:
        illust['local_img'] = download.get_img(url)
    except TimeoutError:
        print('time out retry: %s' % retry)
        if not --retry == 0:
            return download_illust_image(illust, retry)
        else:
            print('time error. url: %s' % url)
            return illust
    print('pixiv dl ok: %s' % url)
    return illust


def tags_list(illust):
    return list(map(lambda t: t.name, illust.tags))


class epixiv(ByPassSniApi):
    search_sort_num: int
    refresh_day: int
    search_sanity_level_count: int
    keyword = ''

    def __init__(self,
                 refresh_day=3,
                 search_sanity_level_count=10
                 ):
        super().__init__(timeout=30)
        self.require_appapi_hosts()
        self.require_appapi_hosts(hostname="public-api.secure.pixiv.net")
        self.refresh_day = refresh_day
        self.search_sanity_level_count = search_sanity_level_count

    @staticmethod
    def illust_is_r18(illust):
        if illust.x_restrict == 1:
            return True
        r18 = ['R-18', 'R18', 'R-18G', 'R18G']
        return any(map(lambda x: x in r18, tags_list(illust)))

    async def search(self, keyword,
                     # 搜索多少页
                     search_sort_num=10,
                     # 安全级别
                     sanity_level=6,
                     # 是否r18
                     is_r18=False
                     ):
        if not keyword:
            return []
        self.keyword = keyword
        res = self.search_illust(keyword)

        if not res.search_span_limit:
            try:
                self.login(config.pixiv.username, config.pixiv.password)
            except Exception as e:
                print('登录p站失败了 请检查配置.')
                return []
            res = self.search_illust(keyword)
            if not res.search_span_limit:
                print('查询出错 请检查账号问题')
                return []

        max_item_size = 30
        total_page = math.ceil(res.search_span_limit / max_item_size)
        workers = min(search_sort_num, total_page)
        pool = ThreadPoolExecutor(max_workers=workers)
        futures = []
        for i in range(workers):
            futures.append(pool.submit(self.search_illust, keyword, offset=max_item_size * i))

        data = []

        for x in as_completed(futures):
            res = x.result()
            if res.get('illusts'):
                data += x.result().illusts
            else:
                print(res)

        data = sorted(data, key=lambda item: item.total_view, reverse=True)
        sl = list(filter(lambda item: item.sanity_level == sanity_level, data))

        while len(sl) < self.search_sanity_level_count and not sanity_level == 0:
            sanity_level -= 2
            sl += list(filter(lambda item: item.sanity_level == sanity_level, data))

        data = sl

        if not is_r18:
            # data = filter(lambda item: item.x_restrict == 0, data)
            data = filter(lambda item: not self.illust_is_r18(item), data)
        else:
            data = filter(lambda item: item.x_restrict == 1, data)

        data = __proxy_illusts_img__(data)

        return data

    @staticmethod
    def download_illusts_img(illusts):
        pool = ThreadPoolExecutor(max_workers=len(illusts))
        futures = []
        for i in illusts:
            futures.append(pool.submit(download_illust_image, util.dict_to_object(i)))

        data = []

        for x in as_completed(futures):
            data.append(x.result())
        return sorted(data, key=lambda item: item.total_view, reverse=True)

    def auto_complete(self, keyword=None):
        keyword = keyword if keyword else self.keyword
        if not keyword:
            return []
        data = []

        url = 'https://jsonp.afeld.me/?url=https://www.pixiv.net/rpc/cps.php?keyword=%s&lang=zh' % parse.quote(keyword)
        ac = util.dict_to_object(requests.get(url, headers={'referer': 'https://www.pixiv.net/'}, timeout=30).json())
        for word in ac.candidates:
            word = util.dict_to_object(word)
            data.append({
                'text': word.tag_name,
                'translation': word.tag_translation or ''
            })
        # url = '%s/v1/search/autocomplete' % self.hosts
        # r = self.no_auth_requests_call('GET', url, params={'word': keyword})
        # ac = self.parse_result(r).search_auto_complete_keywords
        # for word in ac:
        #     data.append({
        #         'text': '',
        #         'translation': word
        #     })

        if len(data) < config.rules.auto_complete_count:
            data += util.filter_list(pixiv_tran, lambda x: keyword in x['translation'])

        data = reduce(lambda x, y: x if y in x else x + [y], [[], ] + data)

        return data[:config.rules.auto_complete_count]

    def get_tag_img(self, keyword=None):
        keyword = keyword if keyword else self.keyword
        if not keyword:
            return None

        url = 'https://jsonp.afeld.me/?url=https://www.pixiv.net/ajax/search/tags/%s' % parse.quote(keyword)
        tag = util.dict_to_object(requests.get(url, headers={'referer': 'https://www.pixiv.net/'}, timeout=30).json())
        if tag.error or isinstance(tag.body.pixpedia, list) or not tag.body.pixpedia.image:
            return None

        img_url = tag.body.pixpedia.image
        local_img = download.get_img(img_proxy(img_url))

        pixpedia = tag.body.pixpedia
        translation = tag.body.tagTranslation[tag.body.tag] if tag.body.tagTranslation else util.Dict({})

        return {
            'tag': tag.body.tag,
            'parentTag': pixpedia.parentTag or '',
            'zh': translation.zh or '',
            'romaji': translation.romaji or '',
            'abstract': pixpedia.abstract or '',
            'local_img': local_img
        }

    def get_meta_pages(self, illust_id):
        if not illust_id:
            return None, []
        info = self.illust_detail(illust_id)
        if info.error:
            print(info.error.user_message)
            return None, []
        illust = info.illust
        illust = __proxy_illusts_img__([illust])[0]
        img_info = get_img_urls(illust)
        images = img_info.meta_pages and list(map(lambda x: x['image_urls']['original'], img_info.meta_pages)) or [
            img_info.original]
        return illust, images

    def recommend(self, illust_id, is_r18=False, can_r18=False):
        info = self.illust_related(illust_id)
        if info.error:
            try:
                self.login(config.pixiv.username, config.pixiv.password)
            except Exception as e:
                print('登录p站失败了 请检查配置.')
                return []
            info = self.illust_related(illust_id)
            if info.error:
                print(info.error.user_message)
                return []

        illusts = sorted(info.illusts, key=lambda item: item.total_view, reverse=True)

        if can_r18:
            return __proxy_illusts_img__(illusts)

        if not is_r18:
            illusts = filter(lambda item: not self.illust_is_r18(item), illusts)
        else:
            illusts = filter(lambda item: item.x_restrict == 1, illusts)

        return __proxy_illusts_img__(illusts)
