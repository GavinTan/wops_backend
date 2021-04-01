from datetime import datetime
from elasticsearch_dsl import Document, Date, Integer, Keyword, Text, connections
from ssl import create_default_context
from django.conf import settings

# context = create_default_context(cafile=f"{settings.BASE_DIR}/apps/kvm/elasticsearch-ca.pem")
# context.check_hostname = False
# Define a default Elasticsearch client ssl_context=context,
connections.create_connection(hosts=['172.16.7.14'], port=9200)


class IUser(Document):
    class Index:
        name = 'iuser'
        settings = {
            "number_of_shards": 2,
            "number_of_replicas": 1
        }

    name = Keyword()
    age = Integer()
    desc = Text(analyzer='ik_max_word', fields={'raw': Keyword()})
    timestamp = Date()

    def save(self, **kwargs):
        return super().save(**kwargs)
