from rest_framework import serializers
from myapp.models import *


class CommentSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='created_by.username')

    class Meta:
        model = Comment
        fields = ('username', 'created_at', 'text', 'id')


class PostSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    created_by = serializers.StringRelatedField()
    
    class Meta:
        model = Post
        fields = ('id', 'title', 'created_by', 'created_at', 'like_count', 'hit_count', 'thumbnail_addr', 'text', 'file_addr', 'tag_string', 'comments')


class TagSerializer(serializers.ModelSerializer):
    posts = PostSerializer(many=True, read_only=True)

    class Meta:
        model = Tag
        fields = ('name', 'posts', 'count')


class LikeSerializer(serializers.ModelSerializer):
    likers = serializers.StringRelatedField(many=True)

    class Meta:
        model = Post
        fields = ('likers', )


class FeedStackSerializer(serializers.ModelSerializer):
    post = PostSerializer(read_only=True)

    class Meta:
        model = Post2Feed
        fields = ('post',)