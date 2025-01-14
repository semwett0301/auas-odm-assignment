class CustomProxyMiddleware(object):
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        middleware = super(CustomProxyMiddleware, cls).__new__(cls)
        middleware.crawler = crawler
        return middleware

    def process_request(self, request, spider):
        request.meta['proxy'] = self.crawler.settings.get("PROXY_URL")
