from django.core.paginator import Paginator, EmptyPage
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from myapp.serializers.user_serializers import *
from myapp.serializers.post_serializers import *
from myapp.models import *
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from django.core.cache import cache
import re

def TagSplitVerifier(tag_string):
    tag_list = tag_string.split("#")
    if len(tag_list) <= 1:
        return (tag_list, False)
    tag_list.pop(0)
    for i in range(len(tag_list)):
        if not bool(re.match('[0-9a-zA-Z가-힣ㄱ-ㅎㅏ-ㅣ_!?]{1,10}$', tag_list[i].strip())) or len(tag_list[i].split()) > 1:
            return (tag_list, False)
        else:
            tag_list[i] = "#" + tag_list[i].strip()
    return (tag_list, True)


def TagValidation(data):
    tag_string = data.get('tag_string')

    if not "#" in tag_string or len(tag_string) > 140:
        return (None, False)

    tag_list, verified = TagSplitVerifier(tag_string)
    if not verified:
        return (None, False)

    return (tag_list, True)