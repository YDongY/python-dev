from rest_framework.routers import DefaultRouter
from . import views

app_name = 'booktest_v2'
urlpatterns = []

router = DefaultRouter()  # 可以处理视图的路由器
router.register('books', views.BookInfoViewSet, basename='books')  # 向路由器中注册视图集

urlpatterns += router.urls  # 将路由器中的所以路由信息追到到 django 的路由列表中
