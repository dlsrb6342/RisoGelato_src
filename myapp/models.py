import datetime
import mimetypes
import os

from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.db import models


def get_upload_path(dirname, obj, filename):
    filename = datetime.datetime.today().isoformat()
    return os.path.join("audiotracks", dirname, obj.created_by.email, filename)


def get_images_upload_path(obj, filename):
    filename = datetime.datetime.today().isoformat()
    return get_upload_path("images", obj, filename)


def get_audio_upload_path(obj, filename):
    filename = datetime.datetime.today().isoformat()
    return get_upload_path("audio_files", obj, filename)


def get_profile_upload_path(obj, filename):
    filename = datetime.datetime.today().isoformat()
    return os.path.join("profilephoto", obj.email, filename)


def get_channelphoto_upload_path(obj, filename):
    filename = datetime.datetime.today().isoformat()
    return os.path.join("channelphoto", obj.admin.email, filename)


class User(AbstractUser):
    """
    Following fields are defined in auth.User model
        username
        email
        password
        is_staff
        date_joined
    """
    live_status = models.BooleanField(default=False)
    following_count = models.PositiveIntegerField(default=0)
    profile_photo_addr = models.ImageField(null=True, upload_to=get_profile_upload_path)

    def __str__(self):
        return self.username


class Post(models.Model):
    title = models.CharField(max_length=50)
    created_by = models.ForeignKey(User, related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)
    like_count = models.PositiveSmallIntegerField(default=0)
    hit_count = models.PositiveSmallIntegerField(default=0)
    thumbnail_addr = models.ImageField(upload_to=get_images_upload_path, null=True, blank=True)
    text = models.TextField()
    tag_string = models.TextField(default=" ")
    file_addr = models.FileField(upload_to=get_audio_upload_path, null=True, blank=True)
    likers = models.ManyToManyField(User, related_name='postLikers', blank=True)

    def get_absolute_url(self):
        return "/risoposts/%i/" % self.id

    @property
    def mimetype(self):
        if not hasattr(self, '_mimetype'):
            self._mimetype = mimetypes.guess_type(self.audio_file.path)[0]
        return self._mimetype

    @property
    def filetype(self):
        if '/' in self.mimetype:
            type_names = {'mpeg': 'MP3', 'ogg': 'Ogg Vorbis'}
            filetype = self.mimetype.split('/')[1]
            return type_names.get(filetype, filetype)
        else:
            return self.mimetype


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments')
    created_by = models.ForeignKey(User)
    created_at = models.DateTimeField(auto_now_add=True)
    text = models.TextField()

    class Meta:
        ordering = ('post', 'created_at')


class Tag(models.Model):
    name = models.CharField(max_length=20)
    count = models.PositiveSmallIntegerField(default=0)
    posts = models.ManyToManyField(Post, related_name="tags", through="Tag2Post", through_fields=('tag', 'post'))


class Tag2Post(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)


class Channel(models.Model):
    admin = models.ForeignKey(User, related_name='channel')
    intro = models.TextField(null=True, help_text="채널의 소개를 작성해주세요.", default="인트로를 작성하세요")
    profile_photo_addr = models.ImageField(upload_to=get_channelphoto_upload_path, null=True)
    follower_count = models.PositiveSmallIntegerField(default=0)
    followers = models.ManyToManyField(User,
                                       through='User2Channel',
                                       through_fields=('channel', 'user'),
                                       related_name="channel_followers")

    class Meta:
        ordering = ('follower_count',)


class FeedStack(models.Model):
    user = models.ForeignKey(User, null=True)
    posts = models.ManyToManyField(Post, through='Post2Feed', through_fields=('stack', 'post'))


class Post2Feed(models.Model):
    stack = models.ForeignKey(FeedStack, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('stack_id', '-post_id')


class User2Channel(models.Model):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Notification(models.Model):
    user = models.ForeignKey(User)
    notifiers = ArrayField(models.PositiveIntegerField(), default=[])
    url = models.TextField()
    notified_at = models.DateTimeField(auto_now_add=True)
    type = models.TextField()
    type_id = models.PositiveIntegerField()

    class Meta:
        ordering = ('-notified_at', )
