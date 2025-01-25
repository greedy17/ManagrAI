import os
import random
from scrapy.utils.request import request_fingerprint
from .constants import USER_AGENT_LIST, REFERER_LIST
from scrapy.dupefilters import RFPDupeFilter


class ClearCacheMiddleware:
    def process_request(self, request, spider):
        if request.url in spider.remove_urls:
            spider_cache_dir = os.path.join(
                spider.crawler.settings.get("HTTPCACHE_DIR", "httpcache"),
                spider.name,  # Assuming each spider has a unique name
            )
            self.remove_cache_for_url(request, spider_cache_dir)

    def remove_cache_for_url(self, request, cache_dir):
        cache_key = self._generate_cache_key(request)
        cache_subdir = os.path.join(cache_dir, cache_key[:2], cache_key)
        if os.path.exists(cache_subdir):
            for file in os.listdir(cache_subdir):
                file_path = os.path.join(cache_subdir, file)
                os.remove(file_path)
            os.rmdir(cache_subdir)

    def _generate_cache_key(self, request):
        # Use Scrapy's request_fingerprint method to generate the key
        return request_fingerprint(request)


class RandomizeHeaderMiddleware:
    def process_request(self, request, spider):
        user_agent = random.choice(USER_AGENT_LIST)
        referer = random.choice(REFERER_LIST)
        dnt = random.choice([0, 1, 3])
        request.headers["User-Agent"] = user_agent
        request.headers["Referer"] = referer
        request.headers["DNT"] = dnt


class CustomDupeFilter(RFPDupeFilter):
    def request_seen(self, request):
        # Allow polling URLs to be requested multiple times
        if request.meta.get("allow_duplicate", False):
            return False
        return super().request_seen(request)
