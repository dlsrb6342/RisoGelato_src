from myapp.views.import_module import *
from myapp.controllers.search_tasks import *
from orderedset import OrderedSet
# from myapp.make_dummy import *


class SearchView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'search/search.html'

    def get(self, request):
        return Response()

    def post(self, request):
        if request.data.get('flag') == 'search':
            search_string = request.data.get('q', '')
            search_result = search.delay(search_string)
            paginator = Paginator(search_result.get(), 11)
            cache.set(request.user.username+'-search', {'page_num': 1, 'paginator': paginator})
            try:
                page = paginator.page(1)
            except EmptyPage:
                return JsonResponse({'flag': False})
            next_page = True
            if not page.has_next():
                next_page = False
            return JsonResponse({ 'results' : page.object_list, 'next_page': next_page, 'flag': True})
        elif request.data.get('flag') == 'search-scrolling':
            page_data = cache.get(request.user.username+'-search')
            page_num = page_data['page_num']
            paginator = page_data['paginator']
            try:
                page = paginator.page(page_num + 1)
            except EmptyPage:
                return Response({'flag': False})
            cache.set(request.user.username+'-search', {'page_num': page_num+1, 'paginator': paginator})
            next_page = True
            if not page.has_next():
                next_page = False
            return JsonResponse({'flag': flag, 'results': page.object_list, 'next_page': next_page})

class TagView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'myapp/tag_detail.html'

    def get(self, request, pk):
        tagname = "#" + pk
        tag = get_object_or_404(Tag, name=tagname)
        serializer = TagSerializer(tag)
        return Response({'tag':serializer.data, 'pk':pk})


class Recommend(APIView):

    def post(self, request):
        if request.data.get('flag') == 'tag':
            tag_list = request.data.getlist('tag_list[]')
            rules = cache.get("recommend_tag_list")

            recommend_list = OrderedSet()
            for rule, confidence in rules:
                tags, results = rule
                if tags and tag_list:
                    if set(tags) == set(tag_list):
                        for result in results:
                            recommend_list.add(result)
                else:
                    return Response({'recommend_tag_list': list(recommend_list)})

            return Response({'recommend_tag_list': list(recommend_list[:5])})

# class DummyData(APIView):
#     def get(self, request):
#         make_post()
#
#         return Response()
