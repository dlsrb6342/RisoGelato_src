from rest_framework import serializers
from myapp.models import *


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        user = User.objects.create(username=validated_data['username'])
        user.set_password(validated_data['password'])
        user.email = validated_data['email']
        user.profile_photo_addr = validated_data['profile_photo_addr']
        user.save()

        return user

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'email', 'live_status', 'following_count', 'profile_photo_addr', 'date_joined',)


class ChannelSerializer(serializers.ModelSerializer):
    admin = serializers.StringRelatedField()

    class Meta:
        model = Channel 
        fields = ('id', 'admin', 'intro', 'profile_photo_addr', 'follower_count',)


class FollowerSerializer(serializers.ModelSerializer):
    followers = serializers.StringRelatedField(many=True)

    class Meta:
        model = Channel
        fields = ('follower_count', 'followers',)


class FollowingSerializer(serializers.ModelSerializer):
    channel = ChannelSerializer(read_only=True)

    class Meta:
        model = User2Channel
        fields = ('channel', )


class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = ('url', 'notified_at')