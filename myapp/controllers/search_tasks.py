from __future__ import absolute_import, unicode_literals
from haystack.query import SearchQuerySet
from celery import shared_task


@shared_task
def search(search_string):
    sqs_post = SearchQuerySet().filter(title__startswith=search_string)[:5]
    sqs_channel = SearchQuerySet().autocomplete(admin_name__startswith=search_string)[:5]
    sqs_tag = SearchQuerySet().autocomplete(name__startswith=search_string)[:5]

    suggestions =[]

    for result in sqs_post:
        d = {"Title": result.title, "id": result.pk}
        suggestions.append(d)

    for result in sqs_channel:
        d = {"Admin": result.admin_name, "id": result.pk}
        suggestions.append(d)

    for result in sqs_tag:
        d = {"Name": result.name, "id": result.pk}
        suggestions.append(d)

    return suggestions