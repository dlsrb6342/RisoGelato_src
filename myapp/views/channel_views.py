from myapp.views.import_module import *


class ChannelDetail(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'myapp/channel_detail.html'

    def get(self, request, pk):
        user = get_object_or_404(User, username=pk)
        channel = get_object_or_404(Channel, admin_id=user.id)
        serializer = ChannelSerializer(channel)
        if request.user in channel.followers.all():
            follow = 1
            if request.user.id == channel.admin.id:
                follow = 2
        else:
            follow = 0
        posts = Post.objects.filter(created_by=channel.admin)
        serializers = PostSerializer(posts, many=True)
        return Response({'Channel': serializer.data,
                         'Follow': follow,
                         'Posts': serializers.data})

    def post(self, request, pk):
        user = get_object_or_404(User, username=pk)
        channel = get_object_or_404(Channel, admin_id=user.id)
        user_id = request.user.id
        username = request.user.username
        admin_id = channel.admin.id
        if request.data.get('flag') == 'follow':
            channel.follower_count += 1
            User2Channel.objects.create(channel_id=channel.id, user_id=user_id)
            admin_posts = Post.objects.filter(created_by=admin_id)
            admin_posts.order_by('-id')[:5]
            feed = FeedStack.objects.get(user=request.user)
            for post in admin_posts:
                Post2Feed.objects.create(post_id=post.id, stack_id=feed.id)
            request.user.following_count += 1
            request.user.save()
            channel.save()
            url = "/channel/" + username + '/'
            notification = Notification.objects.create(user_id=admin_id,
                                                       url=url,
                                                       type="follow",
                                                       type_id=channel.id)
            notification.notifiers.append(user_id)
            notification.save()
            noticount = cache.get(str(admin_id) + "-noticount")
            if noticount:
                cache.set(str(admin_id) + "-noticount", noticount + 1, 90000)
            else:
                cache.set(str(admin_id) + "-noticount", 1, 90000)
            return JsonResponse({'FollowerCount': channel.follower_count})
        elif request.data.get('flag') == 'unfollow':
            channel.follower_count -= 1
            get_object_or_404(User2Channel,
                              channel_id=channel.id,
                              user_id=request.user.id).delete()
            feed = FeedStack.objects.get(user=request.user)
            post2feeds = Post2Feed.objects.filter(stack_id=feed.id)
            for post2feed in post2feeds:
                if post2feed.post.created_by == channel.admin:
                    post2feed.delete()
            request.user.following_count -= 1
            request.user.save()
            channel.save()
            try:
                url = "/channel/" + username + '/'
                notification = Notification.objects.get(user_id=admin_id,
                                                        url=url,
                                                        type="follow",
                                                        type_id=channel.id)
                notification.delete()
            except Exception:
                return JsonResponse({'FollowerCount': channel.follower_count})
            noticount = cache.get(str(admin_id) + "-noticount")
            if noticount:
                cache.set(str(admin_id) + "-noticount", noticount - 1, 90000)
            else:
                cache.set(str(admin_id) + "-noticount", 0, 90000)
            return JsonResponse({'FollowerCount': channel.follower_count})


class FollowerList(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'myapp/follower_list.html'

    def get(self, request, pk):
        user = get_object_or_404(User, username=pk)
        channel = get_object_or_404(Channel, admin_id=user.id)
        serializer = FollowerSerializer(channel)
        return Response({'data': serializer.data,
                         'channel_admin': channel.admin.username})


class ChannelEdit(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'myapp/channel_edit.html'

    def get(self, request, pk):
        user = get_object_or_404(User, username=pk)
        channel = get_object_or_404(Channel, admin_id=user.id)
        serializer = ChannelSerializer(channel)
        return Response({'Channel': serializer.data})

    def post(self, request, pk):
        channel = get_object_or_404(Channel, admin=request.user)
        channel.intro = request.data.get("intro")
        if request.data.get("profile_photo_addr"):
            channel.profile_photo_addr = request.data.get("profile_photo_addr")
        channel.save()
        return redirect('/channel/' + pk + '/')
