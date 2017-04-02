from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from myapp.serializers.post_serializers import *
from datetime import datetime


@shared_task
def create_tag(tag_list, post_id):
    for tag_name in tag_list:
        tag, created = Tag.objects.get_or_create(name=tag_name)
        tag.count += 1
        Tag2Post.objects.create(tag_id=tag.id, post_id=post_id)
        tag.save()


@shared_task
def delete_tag(tag_list):
    for tag_name in tag_list:
        old_tag = get_object_or_404(Tag, name=tag_name)
        old_tag.count -= 1

        if old_tag.count <= 0:
            old_tag.delete()
        else:
            old_tag.save()


@shared_task
def push_feed(follower_id, post_id):
    feedstack = get_object_or_404(FeedStack, user_id=follower_id)
    Post2Feed.objects.create(post_id=post_id, stack_id=feedstack.id)


@shared_task
def send_notification(user_id, notifier_id, post_id, type):
    notification, created = Notification.objects.get_or_create(user_id=user_id,
                                                               url="/posts/"+str(post_id)+'/',
                                                               type=type,
                                                               type_id=post_id)
    notification.notifiers.append(notifier_id)
    notification.notified_at = datetime.now()
    notification.save()
    noticount = cache.get(str(user_id)+"-noticount")
    if noticount:
        cache.set(str(user_id)+"-noticount", noticount+1, 90000)
    else:
        cache.set(str(user_id)+"-noticount", 1, 90000)


@shared_task
def delete_notification(user_id, notifier_id, post_id, type):
    try:
        notification = Notification.objects.get(user_id=user_id,
                                                url="/posts/"+str(post_id)+'/',
                                                type=type,
                                                type_id=post_id)
    except:
        return
    try:
        notification.notifiers.remove(notifier_id)
    except:
        pass

    if len(notification.notifiers) <= 0 :
        notification.delete()
    else:
        notification.save()

    noticount = cache.get(str(user_id)+"-noticount")
    if noticount:
        cache.set(str(user_id)+"-noticount", noticount-1, 90000)
    else:
        cache.set(str(user_id)+"-noticount", 0, 90000)

