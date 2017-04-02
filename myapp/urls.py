from django.conf.urls import url
from myapp.views.post_views import *
from myapp.views.channel_views import *
from myapp.views.user_views import *
from myapp.views.feed_views import *
from myapp.views.search_views import *


urlpatterns = [
    url(r'^$', UserSignIn.as_view(), name='login'),
    url(r'^posts/$', PostList.as_view(), name='post-list'),
    url(r'^posts/(?P<pk>[0-9]+)/$', PostDetail.as_view(), name='post-detail'),
    url(r'^posts/(?P<pk>[0-9]+)/likes/$', LikeList.as_view(), name='like-list'),
    url(r'^posts/(?P<pk>[0-9]+)/edit/$', PostEdit.as_view(), name='post-edit'),
    url(r'^posts/new/$', PostWrite.as_view(), name='post-write'),

    url(r'^users/(?P<pk>[0-9a-zA-Z가-힣ㄱ-ㅎㅏ-ㅣ._@]+)/$', UserDetail.as_view(), name='user-detail'),
    url(r'^user/register/$', UserSignUp.as_view(), name='user-signup'),
    url(r'^user/checkid/$', UserCheckID.as_view(), name='user-checkid'),
    url(r'^user/checkemail/$', UserCheckEmail.as_view(), name='user-checkemail'),
    url(r'^user/auth/$', SendAuthMail.as_view(), name='send-auth-mail'),
    url(r'^user/logout/$', logout, {'next_page': '/'}),
    url(r'^user/complete/$', AfterAuth.as_view(), name='after-auth'),
    url(r'^users/(?P<pk>[0-9a-zA-Z가-힣ㄱ-ㅎㅏ-ㅣ._@]+)/following/$', FollowingList.as_view(), name='following-list'),
    url(r'^users/(?P<pk>[0-9a-zA-Z가-힣ㄱ-ㅎㅏ-ㅣ._@]+)/edit/$', UserEdit.as_view(), name='user-edit'),


    url(r'^channel/(?P<pk>[0-9a-zA-Z가-힣ㄱ-ㅎㅏ-ㅣ._@]+)/$', ChannelDetail.as_view(), name='channel-detail'),
    url(r'^channel/(?P<pk>[0-9a-zA-Z가-힣ㄱ-ㅎㅏ-ㅣ._@]+)/edit/$', ChannelEdit.as_view(), name='channel-edit'),
    url(r'^channel/(?P<pk>[0-9a-zA-Z가-힣ㄱ-ㅎㅏ-ㅣ._@]+)/followers/$', FollowerList.as_view(), name='follower-list'),

    url(r'^feed/$', FeedView.as_view(), name='feed-view'),
    url(r'^tag/(?P<pk>[0-9a-zA-Z가-힣ㄱ-ㅎㅏ-ㅣ_!?]+)/$', TagView.as_view(), name='tag-detail'),

    url(r'notification/$', NotificationView.as_view(), name='notification'),
    url(r'recommend/$', Recommend.as_view(), name='recommend'),
    # url(r'dummy/$', DummyData.as_view(), name='dummy-data')
]
