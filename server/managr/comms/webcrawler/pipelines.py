from dateutil import parser
from ..models import Article, NewsSource
from ..serializers import ArticleSerializer


def data_cleaner(data):
    try:
        article_tags = data.pop("content")
        full_article = ""
        if article_tags is not None:
            for article in article_tags:
                article = article.replace("\n", "").strip()
                full_article += article
            content = full_article.replace("\n", " ").replace("\t", " ").replace("  ", "")
            data["content"] = content
        date = data.pop("publish_date")
        parsed_date = parser.parse(date)
        data["author"] = (
            data["author"].replace("\n", "").replace(" and ", ",").replace("By ,", "").strip()
        )
        authors = data["author"].split(",")
        author = authors[0]
        data["author"] = author
        data["publish_date"] = parsed_date
        if len(data["title"]) > 150:
            data["title"] = data["title"][:145] + "..."
    except KeyError as e:
        return {"data": data, "error": str(e)}
    except parser.ParserError as e:
        return {"data": data, "error": str(e)}
    return data


class BulkInsertPipeline:
    def __init__(self):
        self.items = []
        self.urls = []
        self.errors = {}
        self.index = 1

    def open_spider(self, spider):
        """Called when the spider is opened."""
        self.items = []
        self.errors = {}
        self.urls = spider.start_urls
        self.index = 0

    def close_spider(self, spider):
        """Called when the spider is closed. Perform the bulk insert here."""
        if self.items:
            self.bulk_insert(self.items)
        if self.errors:
            self.add_errors(self.errors)
        print(
            f"===================\nPIPELINE REPORT\nITEMS:{len(self.items)}\nERRORS: {len(self.errors)}\n==================="
        )

    def process_item(self, item, spider):
        """Called for each item. Add it to the collection."""
        self.index += 1
        try:
            cleaned_data = data_cleaner(item)
            if "error" not in cleaned_data.keys():
                if spider.article_only:
                    instance = Article.objects.get(id=item["id"])
                    serializer = ArticleSerializer(
                        instance=instance, data=cleaned_data, partial=True
                    )
                else:
                    serializer = ArticleSerializer(data=cleaned_data)
                if serializer.is_valid():
                    if spider.article_only:
                        serializer.save()
                    else:
                        self.items.append(serializer.validated_data)
            else:
                source_id = item["source"]
                if source_id not in self.errors.keys():
                    self.errors[str(source_id)] = cleaned_data
        except Exception as e:
            print(e)
        return f"Processed: {self.index} urls"

    def bulk_insert(self, items):
        """Perform the bulk insert into the Django model."""
        bulk_data = []
        for art in items:
            bulk_data.append(Article(**art))
        try:
            # Bulk create Django objects
            created_arts = Article.objects.bulk_create(
                bulk_data, ignore_conflicts=True, batch_size=500
            )
            print(f"Successfully inserted {len(created_arts)} items out of {len(self.items)}")
            source_ids = [art.source.id for art in created_arts]
            news = NewsSource.objects.filter(id__in=source_ids)
            for n in news:
                n.crawling
                n.check_if_stopped()
        except Exception as e:
            print(f"Error during bulk insert: {e}")

    def add_errors(self, errors):
        news = NewsSource.objects.filter(id__in=list(errors.keys()))
        for n in news:
            error_data = errors[str(n.id)]
            n.error_log = f"Source: {n.domain} - {error_data}"
            n.save()
