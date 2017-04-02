from haystack import indexes
from myapp.models import *

class PostIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title')

    def get_model(self):
        return Post

    def index_queryset(self, using=None):
        return self.get_model().objects.all()


class ChannelIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    admin_name = indexes.CharField()

    def get_model(self):
        return Channel

    def prepare_admin_name(self, obj):
        return obj.admin.username

    def index_queryset(self, using=None):
        return self.get_model().objects.all().select_related('admin')


class TagIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    name = indexes.CharField(model_attr='name')

    def get_model(self):
        return Tag

    def index_queryset(self, using=None):
        return self.get_model().objects.all()
