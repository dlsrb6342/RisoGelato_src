from __future__ import absolute_import, unicode_literals
from celery.decorators import periodic_task
from celery.task.schedules import crontab
from django.core.cache import cache
from myapp.recommend import recommend_tag, recommend_follow
from datetime import datetime
from pytz import timezone
from datautil.relativedelta import relativedelta


@periodic_task(run_every=(crontab(minute='*/15')))
def make_recommend_tag():
    items, rules = recommend_tag()
    cache.set("recommend_tag_list", rules, 1800)
    return


@periodic_task(run_every=(crontab(minute='7, 22, 37, 52')))
def make_recommend_follow():
    items, rules = recommend_follow()
    cache.set("recommend_follow_list", rules, 1800)
    cache.set("popular_list", items[:100], 1800)
    return


@periodic_task(run_every=(crontab(hour='3')))
def delete_old_feed():
    now = datetime.now().replace(tzinfo=timezone('UTC'))
    past = now - relativedelta(months=3)

    post2feeds = Post2Feed.objects.filter(created_at__lte=past)
    for post2feed in post2feeds:
        post2feed.delete()
    return


@periodic_task(run_every=(crontab(hour='5')))
def delete_old_noti():
    last_user = User.objects.latest('id')
    for i in range(last_user.id + 1):
        noticount = cache.get(i+'noticount')
        if noticount == None:
            continue
        if noticount > 50:
            delete_count = noticount - 40
            notifications = Notification.objects.filter(user_id=i).order_by('notified_at')[:delete_count]
            for notification in notifications:
                notification.delete()
            cache.set(i+'noticount', 40, 90000)
    return
