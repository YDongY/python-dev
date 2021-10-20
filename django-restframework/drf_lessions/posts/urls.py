from django.urls import path
from . import views

app_name = 'posts'
urlpatterns = [
    path('users/', views.user_list, name='user-list'),
    path('users/<pk>/', views.user_detail, name='user-detail'),
    path('rest/users/', views.rest_user_list, name='rest-user-list'),
    path('rest/users/<pk>/', views.rest_user_detail, name='rest-user-detail'),

    path('rest/posts/', views.PostList.as_view(), name='rest-post-list'),
    path('rest/posts/<pk>/', views.PostDetail.as_view(), name='rest-post-detail'),

    path('rest/tags/', views.TagList.as_view(), name='rest-tag-list'),
    path('rest/tags/<pk>/', views.TagDetail.as_view(), name='rest-tag-detail'),

    path('rest/generics/tags/', views.TagGenericsList.as_view(), name='rest-generics-tag-list'),
    path('rest/generics/tags/<pk>/', views.TagGenericsDetail.as_view(), name='rest-generics-tag-detail'),

    path('rest/mixin/users/<pk>/<username>/', views.RetrieveUserView.as_view(), name='rest-mixin-user-detail'),

    # 视图集
    # path('rest/viewset/users/', views.UserViewSet.as_view({'get': 'list'}), name='rest-viewset-user-list'),
    # path('rest/viewset/users/<pk>/', views.UserViewSet.as_view({'get': 'retrieve'}), name='rest-viewset-user-detail'),

    path('rest/template/users/<pk>/', views.UserDetailTemplateHTMLRenderer.as_view(), name='rest-template-user-detail'),
    path('rest/template/users/', views.UserList.as_view(), name='rest-template-user-list'),
]
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# prefix 该视图集的路由前缀 viewset 视图集 base_name 路由名称的前缀
router.register(prefix=r'rest/viewset/users', viewset=views.UserViewSet, basename='rest-viewset-user')

# 相当于上下面通过 path 添加的路由

urlpatterns += router.urls

router.register(prefix=r'rest/modelviewset/users', viewset=views.UserModelViewSet, basename='rest-modelviewset-user')
urlpatterns += router.urls
