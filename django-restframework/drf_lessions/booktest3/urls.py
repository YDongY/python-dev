from django.urls import path
from . import views

app_name = 'booktest_v3'
urlpatterns = [
    # ==================== FBV =============================
    path('fbv/books/', views.fbv_book_list_view, name='fbv_book_list_view'),
    path('fbv/books/<int:pk>/', views.fbv_book_detail_view, name='fbv_book_detail_view'),

    path('cbv/heros/', views.CBVHeroListView.as_view(), name='CBVHeroListView'),
    path('cbv/heros/<int:pk>/', views.CBVGHeroDetailView.as_view(), name='CBVGHeroDetailView'),

    path('gcbv/heros/', views.GCBVHeroListView.as_view(), name='GCBVHeroListView'),
    path('gcbv/heros/<int:pk>/', views.GCBVHeroDetailView.as_view(), name='GCBVHeroDetailView'),

    path('heros/', views.HeroListAPIView.as_view(), name='HeroListAPIView'),

    path('heros-viewset/', views.HeroViewSet.as_view({'get': 'list', 'post': 'create'}), name='HeroViewSet'),
    path('heros-viewset/<int:pk>/',
         views.HeroViewSet.as_view({'get': 'retrieve', 'delete': 'destroy', 'put': 'update'}),
         name='HeroViewSet'),

    path('heros-genericviewset/', views.HeroGenericViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='HeroGenericViewSet'),
    path('heros-genericviewset/<int:pk>/',
         views.HeroGenericViewSet.as_view({'get': 'retrieve', 'delete': 'destroy', 'put': 'update'}),
         name='HeroGenericViewSet'),

    path('heros-modelviewset/', views.HeroModelViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='HeroModelViewSet'),
    path('heros-modelviewset/<int:pk>/',
         views.HeroModelViewSet.as_view({'get': 'retrieve', 'delete': 'destroy', 'put': 'update'}),
         name='HeroModelViewSet'),
]

from rest_framework import routers

router = routers.SimpleRouter()
# prefix 该视图集的路由前缀
# viewset 视图集
# base_name 路由名称的前缀
router.register(prefix='books', viewset=views.HeroModelViewSet, basename='book')

# 最终会形成
# ^books/$        name: book-list
# ^books/{pk}/$   name: book-detail

