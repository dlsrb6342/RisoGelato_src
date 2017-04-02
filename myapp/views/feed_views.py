from myapp.views.import_module import *
from django.http import Http404, HttpResponse
import random

class FeedView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'myapp/feed_view.html'

    def get(self, request):
        feedstack = get_object_or_404(FeedStack, user=request.user)
        post2feeds = Post2Feed.objects.filter(stack_id=feedstack.id)
        if post2feeds.count() > 6 :
            paginator = Paginator(post2feeds, 10)
            cache.set(request.user.username+'-feed', {'page_num': 1, 'paginator': paginator})
            try:
                page = paginator.page(1)
            except EmptyPage:
                return JsonResponse({'flag': False})
            user_like = []
            for post2feed in page:
                if request.user in post2feed.post.likers.all():
                    user_like.append(False)
                else:
                    user_like.append(True)
            next_page = True
            if not page.has_next():
                next_page = False
            serializers = FeedStackSerializer(page, many=True)
            data_user_like = list(zip(serializers.data, user_like))
            return Response({ 'data': data_user_like, 'flag': True, 
                            'next_page': next_page, 'newbie': False })
        else:
            user_like = []
            for post2feed in post2feeds:
                if request.user in post2feed.post.likers.all():
                    user_like.append(False)
                else:
                    user_like.append(True)
            serializers = FeedStackSerializer(post2feeds, many=True)
            data_user_like = list(zip(serializers.data, user_like))
            
            rules = cache.get("recommend_follow_list")
            user2channel_list = User2Channel.objects.filter(user_id=request.user.id)
            followings = []
            for user2channel in user2channel_list:
                if not user2channel.channel.admin.username == request.user.username:
                    followings.append(user2channel.channel.admin.username)

            recommend_list = set()
            k = len(followings)
            print(k)
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

            return Response({ 'data': data_user_like, 
                'recommend_follow_list': return_list, 'newbie': True })



    def post(self, request):
        if request.data.get('flag') == 'comment':
            pk = request.data.get('pk')
            comments = Comment.objects.filter(post_id=pk)
            paginator = Paginator(comments, 7)
            cache.set(request.user.username+'-comment', {'page_num': 1, 'paginator': paginator})
            try:
                page = paginator.page(1)
            except EmptyPage:
                return Response({'flag': False})
            next_page = True
            if not page.has_next():
                next_page = False
            serializers = CommentSerializer(page, many=True)
            return JsonResponse({ 'comments': serializers.data, 'flag': True, 'next_page': next_page })
        elif request.data.get('flag') == 'feed-scrolling':
            page_data = cache.get(request.user.username+'-feed')
            page_num = page_data['page_num']
            paginator = page_data['paginator']
            try:
                page = paginator.page(page_num + 1)
            except EmptyPage:
                return JsonResponse({ 'flag': False })
            cache.set(request.user.username+'-feed', {'page_num': page_num+1, 'paginator': paginator})
            user_like = []
            for post2feed in page:
                if request.user in post2feed.post.likers.all():
                    user_like.append(False)
                else:
                    user_like.append(True)
            next_page = True
            if not page.has_next():
                next_page = False
            serializers = FeedStackSerializer(page, many=True)
            data_user_like = list(zip(serializers.data, user_like))
            return JsonResponse({ 'data': data_user_like, 'flag': True, 'next_page': next_page })
        elif request.data.get('flag') == 'comment-scrolling':
            pk = request.data.get('pk')
            page_data = cache.get(request.user.username+'-comment')
            page_num = page_data['page_num']
            paginator = page_data['paginator']
            try:
                page = paginator.page(page_num + 1)
            except EmptyPage:
                return JsonResponse({ 'flag': False })
            cache.set(request.user.username+'-comment', {'page_num': page_num+1, 'paginator': paginator})
            next_page = True
            if not page.has_next():
                next_page = False
            serializers = CommentSerializer(page, many=True)
            return JsonResponse({ 'comments': serializers.data, 'flag': True, 'next_page': next_page })
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
