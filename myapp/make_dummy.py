from bs4 import BeautifulSoup
import urllib.request
from collections import OrderedDict
import random
import string
from myapp.models import *

def make_user():
    names = read_file()

    cnt = 0
    for name in names:
        cnt += 1
        user = User.objects.create(username=name)
        user.email = email_generator()
        user.set_password('risogelato')
        user.save()
        channel = Channel.objects.create(admin=user)
        User2Channel.objects.create(channel_id=channel.id, user_id=user.id)
        feedstack = FeedStack.objects.create(user=user)
        channel.save()
        feedstack.save()
        if cnt > 300:
            break
    return


def make_post():
    html = open('/home/smilegate/RisoGelato/myapp/Instagram4.html','r').read()
    html_edit = ''
    flag = True
    for a in range(len(html)):
        if html[a:a+4] == '<!--':
            flag = False
        if html[a-3:a] == '-->':
            flag = True

        if flag:
            html_edit += html[a]
    soup = BeautifulSoup(html_edit, "lxml")
    h1_tag = soup.find_all('h1')

    cnt = 0
    for h1 in h1_tag:
        user_id = random.randint(2, 304)
        post = Post.objects.create(created_by_id=user_id)
        post.title = get_title(h1) + str(cnt)
        tag_string, tag_list = get_tag(h1)
        post.tag_string = tag_string
        post.text = get_text(h1)
        post.file_addr = "audiotracks/audio_files/default/default" + str(random.randint(1, 3)) + ".mp3/"
        post.thumbnail_addr = "audiotracks/images/default/default" + str(random.randint(1, 3)) + ".png/"
        post.save()
        feedstack = FeedStack.objects.get(user_id=user_id)
        Post2Feed.objects.create(post_id=post.id, stack_id=feedstack.id)
        channel = Channel.objects.get(admin_id=user_id)
        followers = channel.followers.all()
        for follower in followers:
            if follower.id != user_id:
                feedstack = FeedStack.objects.get(user_id = follower.id)
                Post2Feed.objects.create(post_id=post.id, stack_id=feedstack.id)

        for tag_name in tag_list:
            if len(tag_name) < 19 :
                tag, created = Tag.objects.get_or_create(name=tag_name)
                tag.count += 1
                Tag2Post.objects.create(tag_id=tag.id, post_id= post.id)
                tag.save()
    return


def email_generator(size=7, chars=string.ascii_lowercase + string.digits):
    email = random.choice(string.ascii_uppercase) + ''.join(random.choice(chars) for _ in range(size))
    email += '@risogelato.com'
    return email


def get_text(h1):
    text = h1.span
    return text.text if text.text else 'Hello World!'


def get_title(h1):
    title = h1.a.extract()
    return title['title']


def get_tag(h1):
    tag_string = ''
    tag_list = []
    while True:
        try:
            tag = h1.a.extract()
        except Exception:
            break
        if not '@' in tag.text:
            tag_string += tag.text + ' '
            tag_list.append(tag.text)
    return tag_string, tag_list


def read_file():
    file_iter = open('/home/smilegate/RisoGelato/myapp/Person.csv', 'r')
    names = []
    for line in file_iter:
        line = line.split(',')
        name = line[0]
        names.append(name)
    name_set = set()
    for i in range(300):
        name_set.add(names[random.randint(0,196460)])
    return list(name_set)


def make_follow():
    for i in range(10000):
        user_id = random.randint(2,304)
        channel_id = random.randint(1,303)
        # if user_id == 227:
        #     continue
        user2channel, created = User2Channel.objects.get_or_create(channel_id=channel_id, user_id=user_id)
        if created:
            user = User.objects.get(pk=user_id)
            channel = Channel.objects.get(pk=channel_id)
            user.following_count += 1
            channel.follower_count += 1
            user.save()
            channel.save()
            # admin_posts = Post.objects.filter(created_by=channel.admin.id).order_by('-id')[:5]
            # feed = FeedStack.objects.get(user=user)
            # for post in admin_posts:
            #     Post2Feed.objects.create(post_id=post.id, stack_id=feed.id)
    return
