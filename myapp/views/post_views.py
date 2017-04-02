from myapp.controllers.post_tasks import *
from django.core.files.base import File
from myapp.views.import_module import *
import io
import base64

class PostList(APIView):

    def post(self, request):
        pk = request.data.get('pk')
        if not pk:
            post = Post.objects.create(created_by=request.user)
            try:
                serializer = PostSerializer(post, data=request.data)
            except Exception:
                post.delete()
                return Response(status=status.HTTP_400_BAD_REQUEST)
            if serializer.is_valid():
                tag_list, valid = TagValidation(request.data)
                if not valid:
                    post.delete()
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                else:
                    base_64 = request.data.get('base64')
                    audiofile_byte = base64.b64decode(base_64)
                    with io.BytesIO(audiofile_byte) as stream:
                        blob_file = File(stream)
                        post.file_addr.save('file.ogg', blob_file)
                    create_tag.delay(tag_list, post.id)
                    serializer.save()
                    channel = get_object_or_404(Channel, admin=request.user)
                    followers = channel.followers.all()
                    for follower in followers:
                        if follower.id != request.user.id:
                            push_feed.delay(follower.id, post.id)
                        else:
                            feedstack = get_object_or_404(FeedStack, user_id=follower.id)
                            Post2Feed.objects.create(post_id=post.id, stack_id=feedstack.id)
                    return redirect('/feed/')
            else:
                post.delete()
                return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            post = get_object_or_404(Post, pk=pk)
            tag_list, trash = TagSplitVerifier(post.tag_string)
            delete_tag.delay(tag_list)
            post.delete()
            return redirect('/feed/')


class PostWrite(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'myapp/post_upload.html'

    def get(self,request):
        return Response()


class PostDetail(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'myapp/post_detail.html'

    def post(self, request, pk):
        if request.data.get('flag') == 'like':
            post = get_object_or_404(Post, pk=pk)
            post.like_count += 1
            post.likers.add(request.user)
            post.save()
            serializer = PostSerializer(post)
            if post.created_by_id != request.user.id:
                send_notification.delay(post.created_by_id, request.user.id, post.id, "like")
            return Response()
        elif request.data.get('flag') == 'unlike':
            post = get_object_or_404(Post, pk=pk)
            post.like_count -= 1
            post.likers.remove(request.user)
            post.save()
            serializer = PostSerializer(post)
            if post.created_by_id != request.user.id:
                delete_notification.delay(post.created_by_id, request.user.id, post.id, "like")
            return Response()
        elif request.data.get('flag') == 'comment':
            text = request.data.get('text')
            post = get_object_or_404(Post, pk=pk)
            comment = Comment.objects.create(text=text, post = post, created_by=request.user)
            comment.save()

            if request.user in post.likers.all():
                user_like = False
            else:
                user_like = True
            serializer = PostSerializer(post)
            if post.created_by_id != request.user.id:
                send_notification.delay(post.created_by_id, request.user.id, post.id, "comment")
            return JsonResponse({'cid':comment.id})
        elif request.data.get('flag') == 'edit':
            post = get_object_or_404(Post, pk=pk)

            data = request.data
            post.title = data.get('title')
            post.text = data.get('text')
            old_tag_string = post.tag_string
            post.tag_string = data.get('tag_string')
            new_tag_list, valid = TagValidation(data)
            serializer = PostSerializer(post)
            if not valid:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            post.save()
            old_tag_list, trash = TagSplitVerifier(old_tag_string)
            create_tag.delay(new_tag_list, post.id)
            delete_tag.delay(old_tag_list)
            if request.user in post.likers.all():
                user_like = False
            else:
                user_like = True
            return Response({'post':serializer.data, 'UserLike':user_like, 'pk':pk})


    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        if request.user in post.likers.all():
            user_like = False
        else:
            user_like = True
        serializer = PostSerializer(post)
        return Response({'post':serializer.data, 'UserLike':user_like, 'pk':pk})


    def put(self, request, pk):
        if request.data.get('flag') == 'co-edit':
            comment = get_object_or_404(Comment, id=request.data.get('cid'))
            comment.text = request.data.get('text')
            comment.save()
            return Response()


    def delete(self, request, pk):
        if request.data.get('flag') == 'co-delete':
            post = Post.objects.get(pk=pk)
            comment = get_object_or_404(Comment, id=request.data.get('cid'))
            comment.delete()
            if post.created_by_id != request.user.id:
                delete_notification.delay(post.created_by_id, request.user.id, post.id, "comment")
            return Response()
        

class PostEdit(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'myapp/post_edit.html'

    def get(self,request, pk):
        post = get_object_or_404(Post, pk=pk)
        serializer = PostSerializer(post)
        return Response({'post':serializer.data, 'pk':pk})
        

class LikeList(APIView):

    def post(self, request, pk):
        if request.data.get('flag') == "likelist":
            post = Post.objects.get(pk=pk)
            serializer = LikeSerializer(post)
            paginator = Paginator(serializer.data['likers'], 10)
            cache.set(request.user.username + '-likers', {'page_num': 1, 'paginator': paginator})
            try:
                page = paginator.page(1)
            except EmptyPage:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            next_page = True
            if not page.has_next():
                next_page = False
            return JsonResponse({'likers':page.object_list, 'next_page':next_page})

        if request.data.get('flag') == "likelist-scrolling":
            page_data = cache.get(request.user.username+'-likers')
            page_num = page_data['page_num']
            paginator = page_data['paginator']
            try:
                page = paginator.page(page_num + 1)
            except EmptyPage:
                return JsonResponse(status=status.HTTP_400_BAD_REQUEST)
            next_page = True
            if not page.has_next():
                next_page = False
            cache.set(request.user.username + '-likers', {'page_num': page_num+1, 'paginator': paginator})
            return JsonResponse({ 'likers': page.object_list, 'next_page': next_page })
