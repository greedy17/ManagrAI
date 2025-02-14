import math
from datetime import datetime, timedelta
from urllib.parse import urlparse

from dateutil import parser
from django.contrib.postgres.fields import JSONField
from django.contrib.postgres.search import SearchVector, SearchVectorField
from django.db import models
from django.db.models.constraints import UniqueConstraint

from managr.comms.webcrawler.extractor import SourceExtractor
from managr.core.models import TimeStampModel


class NewsSourceQuerySet(models.QuerySet):
    def active(self, extra_filters=None):
        active_sources = self.filter(is_active=True, is_crawling=True, use_scrape_api=False)
        if extra_filters:
            active_sources = active_sources.filter(**extra_filters)
        return active_sources

    def scrape_api(self, extra_filters=None):
        scrape_sources = self.filter(is_active=True, is_crawling=True, use_scrape_api=True)
        if extra_filters:
            scrape_sources = scrape_sources.filter(**extra_filters)
        return scrape_sources

    def stopped(self, extra_filters=None):
        stopped_sources = self.filter(is_crawling=True, is_active=True, is_stopped=True)
        if extra_filters:
            stopped_sources = stopped_sources.filter(**extra_filters)
        return stopped_sources

    def as_list(self):
        domains = self.values_list("domain", flat=True)
        return list(domains)


class NewsSource(TimeStampModel):
    domain = models.CharField(max_length=255, unique=True)
    site_name = models.CharField(max_length=255, blank=True, null=True)
    sitemap = models.CharField(max_length=255, blank=True, null=True)
    last_scraped = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_crawling = models.BooleanField(default=False)
    is_stopped = models.BooleanField(default=False)
    use_scrape_api = models.BooleanField(default=False)
    posting_frequency = models.IntegerField(default=0)
    scrape_type = models.CharField(
        choices=[("HTML", "HTML"), ("SITEMAP", "Sitemap"), ("XML", "XML")],
        max_length=50,
        default="HTML",
    )
    access_count = JSONField(default=dict, null=True, blank=True)
    icon = models.TextField(null=True, blank=True)
    # Web Scraping Fields
    category_link_selector = models.CharField(max_length=255, blank=True, null=True)
    category_name_attribute = models.CharField(max_length=50, blank=True, null=True)
    category_mapping = JSONField(
        blank=True,
        null=True,
        help_text="JSON mapping of website categories to application categories",
    )
    article_link_selector = models.CharField(max_length=255, blank=True, null=True)
    article_link_attribute = models.CharField(max_length=50, blank=True, null=True)
    article_link_prefix = models.URLField(blank=True, null=True)
    article_link_regex = models.CharField(max_length=500, blank=True, null=True)
    data_attribute_key = models.CharField(max_length=255, blank=True, null=True)
    data_attribute_value = models.CharField(max_length=255, blank=True, null=True)
    date_published_selector = models.CharField(max_length=255, blank=True, null=True)
    date_published_format = models.CharField(max_length=255, blank=True, null=True)
    article_title_selector = models.CharField(max_length=255, blank=True, null=True)
    article_content_selector = models.CharField(max_length=255, blank=True, null=True)
    author_selector = models.CharField(max_length=255, blank=True, null=True)
    description_selector = models.CharField(max_length=255, blank=True, null=True)
    image_url_selector = models.CharField(max_length=255, blank=True, null=True)
    scrape_data = JSONField(default=dict, null=True, blank=True)
    error_log = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.domain

    objects = NewsSourceQuerySet.as_manager()

    class Meta:
        ordering = ["-datetime_created"]

    def extractor(self, response):
        return SourceExtractor(response, self)

    @property
    def crawling(self):
        article_check = True if self.articles.first() else False
        self.is_crawling = article_check
        self.save()
        return article_check

    @property
    def selectors_defined(self):
        selector_obj = self.article_selectors
        for value in selector_obj.values():
            if value is None:
                return False
        return True

    @property
    def article_selectors(self):
        return {
            "author": self.author_selector,
            "publish_date": self.date_published_selector,
            "title": self.article_title_selector,
            "content": self.article_content_selector,
            "image_url": self.image_url_selector,
            "description": self.description_selector,
        }

    def _initialize(self, response):
        return self.extractor(response).parse()

    def initialize(self, response):
        if self.last_scraped and self.article_link_regex:
            return self
        return self._initialize(response)

    def get_selectors(self, response):
        if self.selectors_defined:
            return self, self.article_selectors
        else:
            return self.extractor(response).add_selectors()

    def transfer_dict(self):
        return dict(
            domain=self.domain,
            site_name=self.site_name,
            last_scraped=str(self.last_scraped),
            article_link_selector=self.article_link_selector,
            article_link_attribute=self.article_link_attribute,
            article_link_regex=self.article_link_regex,
            data_attribute_key=self.data_attribute_key,
            data_attribute_value=self.data_attribute_value,
            date_published_selector=self.date_published_selector,
            author_selector=self.author_selector,
            article_content_selector=self.article_content_selector,
            is_active=self.is_active,
            use_scrape_api=self.use_scrape_api,
            article_title_selector=self.article_title_selector,
            image_url_selector=self.image_url_selector,
            description_selector=self.description_selector,
        )

    @classmethod
    def domain_list(
        cls,
        scrape_ready=True,
        run_now=False,
        type="HTML",
        is_crawling=True,
        scrape_api=False,
        as_queryset=False,
    ):
        six_hours = datetime.now() - timedelta(hours=6)
        sources = cls.objects.filter(
            is_active=scrape_ready,
            scrape_type=type,
            is_crawling=is_crawling,
            use_scrape_api=scrape_api,
        )
        if settings.IN_DEV or run_now:
            ready_sources = sources.filter(is_crawling=True)
        else:
            ready_sources = sources.filter(is_crawling=True, is_stopped=False).filter(
                last_scraped__lt=six_hours
            )
        if as_queryset:
            return ready_sources
        source_list = [source.domain for source in ready_sources]
        return source_list

    @classmethod
    def problem_urls(cls):
        d = datetime.now().date()
        news = NewsSource.objects.filter(last_scraped__date=d, is_active=False).values_list(
            "domain", flat=True
        )
        return list(news)

    @property
    def newest_article_date(self):
        if self.articles.first():
            return self.articles.first().publish_date
        return None

    def add_error(self, error):
        self.error_log += f"\n{error}"
        return self.error_log

    def sync_journalists(self):
        from managr.comms.models import Journalist
        from managr.comms.serializers import JournalistSerializer

        parsed_domain = urlparse(self.domain)
        domain = parsed_domain.netloc
        articles = self.articles.all().values_list("author", flat=True)
        author_set = list(set(articles))
        for a in author_set:
            if "staff" in a.lower() or self.site_name in a or "The " in a:
                continue
            try:
                if " and " in a:
                    author_list = a.split(" and ")
                else:
                    author_list = a.split(",")
            except ValueError as e:
                print(f"{a} - {e}")
                continue
            for author in author_list:
                try:
                    author_names = author.split(" ")
                    if len(author_names) == 2:
                        first = author_names[0]
                        last = author_names[1]
                    elif len(author_names) == 3:
                        first = author_names[0]
                        if "II" in author_names[2]:
                            last = author_names[1]
                        else:
                            last = author_names[2]
                    else:
                        first = author_names[0]
                        last = author_names[1:]
                    journalist_check = Journalist.objects.filter(first_name=first, last_name=last)
                    if len(journalist_check):
                        continue
                    response = Journalist.email_finder(domain, first, last)
                    if "score" in response.keys() and response["score"] is not None:
                        is_valid = (
                            False
                            if response["verification"]["status"] in ["invalid", "unknown"]
                            else True
                        )
                        data = {
                            "verified": is_valid,
                            "first_name": response["first_name"],
                            "last_name": response["last_name"],
                            "email": response["email"],
                            "outlet": response["company"],
                            "accuracy_score": response["score"],
                            "number_of_sources": len(response["sources"]),
                        }
                        serializer = JournalistSerializer(data=data)
                        serializer.is_valid(raise_exception=True)
                        serializer.save()
                    else:
                        print(f"Failed to find journalist: {response}")
                except ValueError as e:
                    print(f"Failed to split author name: {author} - {e}")
                except Exception as e:
                    print(f"{author} - {e}")
                    continue
        return

    def calculate_posting_frequency(self):
        alpha = 0.3
        publish_dates = list(self.articles.all().values_list("publish_date", flat=True))
        parsed_dates = []
        for date in publish_dates:
            try:
                parsed_dates.append(datetime.strptime(str(date), "%Y-%m-%d %H:%M:%S.%f"))
            except ValueError:
                parsed_dates.append(datetime.strptime(str(date), "%Y-%m-%d %H:%M:%S"))
        unique_dates = sorted({date.date() for date in parsed_dates})
        if len(unique_dates) <= 1:
            return f"Not enough articles synced for {self.domain}"
        time_diffs = [
            (unique_dates[i] - unique_dates[i - 1]).days for i in range(1, len(unique_dates))
        ]
        if len(time_diffs):
            ema = time_diffs[0]
            for diff in time_diffs[1:]:
                ema = alpha * diff + (1 - alpha) * ema
            self.posting_frequency = math.ceil(ema)
        else:
            print(f"Unique: {unique_dates}\nTime Diffs: {time_diffs}")
        return self.save()

    def check_if_stopped(self):
        if self.posting_frequency == 0:
            return
        newest_article = self.newest_article_date
        if newest_article:
            article_date = newest_article.date()
            today = datetime.now().date()
            days_since_last_article = (today - article_date).days
            if days_since_last_article > self.posting_frequency:
                self.is_stopped = True
                if days_since_last_article > 30:
                    self.is_active = False
            else:
                self.is_stopped = False
        self.save()
        return self.is_stopped


class Article(TimeStampModel):
    title = models.CharField(max_length=150)
    description = models.TextField(null=True)
    author = models.CharField(max_length=150, blank=True, null=True)
    publish_date = models.DateTimeField()
    link = models.CharField(max_length=255)
    image_url = models.CharField(max_length=500)
    source = models.ForeignKey(
        "comms.NewsSource", on_delete=models.CASCADE, related_name="articles"
    )
    content = models.TextField()
    content_search_vector = SearchVectorField(null=True)

    class Meta:
        constraints = [UniqueConstraint(fields=["source", "title"], name="unique_article")]
        ordering = ["-publish_date"]

    def update_search_vector(self):
        try:
            self.content_search_vector = SearchVector("content")
            self.save()
        except Exception as e:
            return str(e)
        return True

    def fields_to_dict(self, internal_flag=True):
        site_name = (
            self.source.site_name if hasattr(self.source, "site_name") else self.source.domain
        )
        fields = dict(
            title=self.title,
            description=self.description,
            author=self.author,
            publish_date=str(self.publish_date),
            link=self.link,
            image_url=self.image_url,
            source={"name": site_name, "icon": self.source.icon},
        )
        if internal_flag:
            fields["i"] = True
        return fields

    @classmethod
    def search_by_query(
        cls, boolean_string, date_to=False, date_from=False, author=False, for_report=False
    ):
        from managr.comms.utils import boolean_search_to_query, boolean_search_to_searchquery

        date_to_date_obj = parser.parse(date_to)
        day_incremented = date_to_date_obj + timedelta(days=1)
        day_incremented_str = str(day_incremented)
        date_range_articles = Article.objects.filter(
            publish_date__range=(date_from, day_incremented_str)
        )
        if author:
            boolean_string = boolean_string.replace("journalist:", "").strip()
            articles = date_range_articles.filter(author__icontains=boolean_string)
        else:
            converted_boolean = boolean_search_to_query(boolean_string)
            articles = date_range_articles.filter(converted_boolean)
        if for_report:
            articles = articles[:100]
        else:
            articles = articles[:20]
        return list(articles)


class ArchivedArticle(TimeStampModel):
    archived_on = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=150)
    description = models.TextField(null=True)
    author = models.CharField(max_length=150, blank=True, null=True)
    publish_date = models.DateTimeField()
    link = models.CharField(max_length=255)
    image_url = models.CharField(max_length=500)
    source = models.ForeignKey(
        "comms.NewsSource", on_delete=models.CASCADE, related_name="archived"
    )
    content = models.TextField()
