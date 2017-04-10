from myapp.views.import_module import *
from django.contrib.auth.views import logout
from django.contrib.auth import authenticate, login
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from base64 import b64decode
from myapp.controllers.user_tasks import *
import uuid
import random
from myapp.recommend import *


class UserDetail(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'myapp/user_detail.html'

    def get(self, request, pk):
        user = get_object_or_404(User, username=pk)
        serializer = UserSerializer(user)
        return Response({'user': serializer.data})

    def put(self, request, pk):
        user = get_object_or_404(User, username=pk)
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'user': serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserEdit(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'myapp/user_edit.html'

    def get(self, request, pk):
        user = get_object_or_404(User, username=pk)
        serializer = UserSerializer(user)
        return Response({ 'user':serializer.data })

    def post(self, request, pk):
        user = get_object_or_404(User, username=pk)
        data = request.data
        user.username = data.get('username')
        if data.get('profile_photo_addr'):
            user.profile_photo_addr = data.get('profile_photo_addr')
        user.save()
        return redirect('/users/'+user.username)


class UserSignUp(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'myapp/signup.html'

    def get(self,request):
        return Response()


class AfterAuth(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'myapp/after_auth.html'

    def get(self, request):
        data = cache.get(request.GET['token'])
        if data:
            cache.delete(request.GET['token'])
            user = User.objects.create()
            user.username = data['username']
            user.set_password(data['password'])
            user.email = data['email']
            user.save()
            channel = Channel.objects.create(admin=user)
            User2Channel.objects.create(channel_id=channel.id, user_id=user.id)
            feedstack = FeedStack.objects.create(user=user)
            channel.save()
            feedstack.save()
            return Response({'auth': True})
        else:
            return Response({'auth': False})


class SendAuthMail(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'myapp/before_auth.html'

    def get(self, request):
        return Response(status=status.HTTP_201_CREATED)

    def post(self, request):
        data = request.data.copy()
        password = data['password']
        text = b64decode(password.encode())
        with open('/home/smilegate/rsa_1024_priv.pem', 'rb') as f:
            key = f.read()
        decrypted = decrypt(key, text)
        decrypted = decrypted.decode("utf-8")
        data['password'] = decrypted
        token = str(uuid.uuid4()).replace("-", "")
        cache.set(token, data, 300)
        send_mail.delay(token, data['email'])
        return Response(status=status.HTTP_201_CREATED)


class UserCheckID(APIView):

    def post(self, request):
        username = request.data.get('username')
        cnt = User.objects.filter(username=username).count()

        if cnt != 0:
            return Response({'result': False})
        else:
            return Response({'result': True})


class UserCheckEmail(APIView):

    def post(self, request):
        email = request.data.get('email')
        cnt = User.objects.filter(email=email).count()

        if cnt != 0:
            return Response({'result': False})
        else:
            return Response({'result': True})


class UserSignIn(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'myapp/login.html'

    def get(self, request):
        return Response()

    def delete(self, request):
        request.user.is_active = False
        request.user.save()
        logout(request)
        return Response()

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = User.objects.get(email=email)

        text = b64decode(password.encode())
        with open('/home/smilegate/rsa_1024_priv.pem', 'rb') as f:
            key = f.read()

        decrypted = decrypt(key, text)
        decrypted = decrypted.decode("utf-8")
        user = authenticate(username=user.username, password=decrypted)
        if user is not None:
            if user.is_active:
                login(request, user)
                return Response()
        return Response(status=status.HTTP_400_BAD_REQUEST)


class FollowingList(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'myapp/following_list.html'

    def get(self, request, pk):
        user2channels = User2Channel.objects.filter(user_id=request.user.id)
        following_paginator = Paginator(user2channels, 15)
        cache.set(request.user.username+'-following', {'page_num': 1, 'paginator': following_paginator})
        try:
            following_page = following_paginator.page(1)
        except EmptyPage:
            return JsonResponse({'flag': False})
        serializers = FollowingSerializer(following_page, many=True)
        next_page = True
        if not following_page.has_next():
            next_page = False

        rules = cache.get("recommend_follow_list")
        user2channel_list = User2Channel.objects.filter(user_id=request.user.id)
        followings = []
        for user2channel in user2channel_list:
            if not user2channel.channel.admin.username == request.user.username:
                followings.append(user2channel.channel.admin.username)

        recommend_list = set()
        k = len(followings)
        for _ in range(k):
            while True:
                pick1 = followings[random.randint(0, len(followings) - 1)]
                pick2 = followings[random.randint(0, len(followings) - 1)]
                if pick1 != pick2:
                    break
            following_set = set([pick1, pick2])

            for rule, confidence in rules:
                users, results = rule
                if set(users) == following_set:
                    for result in results:
                        if result not in followings:
                            recommend_list.add((result, confidence))
        def val(tup):
            return tup[1]
        recommend_list = sorted(recommend_list, key=val)
        return_list = list()
        for recommend, conf in recommend_list:
            return_list.append(recommend)

        if len(return_list) <= 15:
            popular_list = cache.get("popular_list")
            while len(return_list) < 15:
                popular = popular_list[random.randint(0, len(popular_list) - 1)][0][0]
                if popular not in followings and popular not in return_list:
                    return_list.append(popular)


        return Response({'next_page':next_page,
                         'data':serializers.data,
                         'following_count': request.user.following_count,
                         'recommend_follow_list': return_list})

    def post(self, request, pk):
        if request.data.get('flag') == 'following-scrolling':
            page_data = cache.get(request.user.username+'-following')
            page_num = page_data['page_num']
            paginator = page_data['paginator']
            try:
                page = paginator.page(page_num + 1)
            except EmptyPage:
                return JsonResponse({ 'flag': False })
            next_page = True
            if not page.has_next():
                next_page = False
            cache.set(request.user.username+'-following', {'page_num': page_num+1, 'paginator': paginator})
            serializers = FollowingSerializer(page, many=True)
            return JsonResponse({'next_page' : next_page, 'data': serializers.data, 'flag': True })


class NotificationView(APIView):

    def notification_message(self, notifications):
        messages = []
        for notification in notifications:
            notifiers_set = set(notification.notifiers)
            message = ''
            if notification.type == 'like':
                if len(notifiers_set) > 1:
                    message += User.objects.get(pk=notification.notifiers[-1]).username + "님 외 "
                    count = len(notifiers_set)
                    message += str(count-1) + "명이 "
                else:
                    message += User.objects.get(pk=notification.notifiers[0]).username + "님이 "
                    count = 1
                type = 'like'
                message += "당신의 목소리를 좋아합니다."
            elif notification.type == 'comment':
                if len(notifiers_set) > 1:
                    message += User.objects.get(pk=notification.notifiers[-1]).username + "님 외 "
                    count = len(notifiers_set)
                    message += str(count-1) + "명이 "
                else:
                    message += User.objects.get(pk=notification.notifiers[0]).username + "님이 "
                    count = 1
                type = 'comment'
                message += "댓글을 남겼습니다."
            elif notification.type == "follow":
                message += User.objects.get(pk=notification.notifiers[0]).username
                message += "님이 당신의 채널을 팔로우했습니다."
                count = 0
                type = 'follow'

            messages.append([message, count, type])

        return messages



    def post(self, request):
        if request.data.get('flag') == 'noti':
            user = request.user
            notifications = Notification.objects.filter(user_id=user.id)
            serializers = NotificationSerializer(notifications, many=True)
            messages = self.notification_message(notifications)
            data = list(zip(serializers.data, messages))
            noti_paginator = Paginator(data, 5)
            cache.set(user.username+'-noti', {'page_num': 1, 'paginator': noti_paginator})
            try:
                page = noti_paginator.page(1)
            except EmptyPage:
                return JsonResponse({'flag': False})
            next_page = True
            if not page.has_next():
                next_page = False
            return JsonResponse({ 'data':page.object_list, 'next_page':next_page, 'flag': True })
        elif request.data.get('flag') == 'noti-scrolling':
            page_data = cache.get(request.user.username+'-noti')
            page_num = page_data['page_num']
            paginator = page_data['paginator']
            try:
                page = paginator.page(page_num + 1)
            except EmptyPage:
                return JsonResponse({ 'flag': False })
            next_page = True
            if not page.has_next():
                next_page = False
            cache.set(request.user.username+'-noti', {'page_num': page_num+1, 'paginator': paginator})
            return JsonResponse({'next_page' : next_page, 'data': page.object_list, 'flag': True })





def decrypt(key, text):
    if type(key) == str:
        key = key.encode()
    if type(text) == str:
        text = text.encode()

    rsakey = RSA.importKey(key)
    rsakey = PKCS1_v1_5.new(rsakey)
    d = rsakey.decrypt(text, 'bollox')
    return d
