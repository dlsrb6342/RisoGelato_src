from django.contrib import admin
from myapp.models import *

# Register your models here.
admin.site.register(Tag)
admin.site.register(User)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Channel)
admin.site.register(FeedStack)
admin.site.register(Post2Feed)
