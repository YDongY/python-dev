from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import BookInfoSerializer, HeroInfoSerializer, HeroInfoModelSerializer
from booktest.models import BookInfo, HeroInfo


@api_view(['GET', 'POST'])
def fbv_book_list_view(request):
    if request.method == "GET":
        books = BookInfo.objects.all()
        serializer = BookInfoSerializer(instance=books, many=True)  # many=True 表示序列化多个对象
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    elif request.method == "POST":
        serializer = BookInfoSerializer(data=request.data)
        # raise_exception 表示检验失败，返回 400
        if serializer.is_valid(raise_exception=True):
            serializer.save()  # 调用 Serializer.create() 方法
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        # print(serializer.errors)  验证结果信息 {'btitle': [ErrorDetail(string='This field is required.', code='required')]}
        # print(serializer.validated_data)  # 验证通过的字段 OrderedDict([('btitle', '连城诀')])


@api_view(['GET', 'PUT', 'DELETE'])
def fbv_book_detail_view(request, pk):
    book = BookInfo.objects.filter(pk=pk).first()
    if not book:
        return Response(data={'error': '没有该图书'}, status=status.HTTP_404_NOT_FOUND)
    if request.method == "GET":
        serializer = BookInfoSerializer(instance=book)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    elif request.method == "PUT":
        serializer = BookInfoSerializer(instance=book, data=request.data, partial=True)  # partial=True 部分更新
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == "DELETE":
        book.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# -------------------------------------------------------------------------------------------------

from rest_framework.views import APIView


class CBVHeroListView(APIView):
    def get(self, request):
        heros = HeroInfo.objects.all()
        serializer = HeroInfoSerializer(instance=heros, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = HeroInfoSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)


class CBVGHeroDetailView(APIView):

    def get(self, request, pk):
        hero = HeroInfo.objects.filter(pk=pk).first()
        if not hero:
            return Response(data={'error': '没有该英雄'}, status=status.HTTP_404_NOT_FOUND)
        serializer = HeroInfoSerializer(instance=hero)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        hero = HeroInfo.objects.filter(pk=pk).first()
        if not hero:
            return Response(data={'error': '没有该英雄'}, status=status.HTTP_404_NOT_FOUND)
        serializer = HeroInfoSerializer(instance=hero, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        hero = HeroInfo.objects.filter(pk=pk).first()
        if not hero:
            return Response(data={'error': '没有该英雄'}, status=status.HTTP_404_NOT_FOUND)
        hero.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# -------------------------------------------------------------------------------------------------

from rest_framework.generics import GenericAPIView


class GCBVHeroListView(GenericAPIView):
    queryset = HeroInfo.objects.all()
    serializer_class = HeroInfoModelSerializer

    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)


class GCBVHeroDetailView(GenericAPIView):
    queryset = HeroInfo.objects.all()
    serializer_class = HeroInfoModelSerializer
    lookup_field = 'pk'

    def get(self, request, pk):
        hero = self.get_object()  # get_object() 方法根据 lookup_field 参数查找 queryset 中的数据对象
        if not hero:
            return Response(data={'error': '没有该英雄'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(hero)
        return Response(serializer.data)

    def put(self, request, pk):
        hero = self.get_object()
        if not hero:
            return Response(data={'error': '没有该英雄'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(instance=hero, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        hero = self.get_object()
        if not hero:
            return Response(data={'error': '没有该英雄'}, status=status.HTTP_404_NOT_FOUND)
        hero.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# -------------------------------------------------------------------------------------------------

from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveAPIView, RetrieveUpdateAPIView, \
    RetrieveUpdateDestroyAPIView, RetrieveDestroyAPIView, CreateAPIView, DestroyAPIView


class HeroListAPIView(ListAPIView):
    queryset = HeroInfo.objects.all()
    serializer_class = HeroInfoModelSerializer


# -------------------------------------------------------------------------------------------------
from rest_framework.viewsets import ViewSet


class HeroViewSet(ViewSet):
    """ViewSet 映射处理工作"""

    def create(self, request, *args, **kwargs):
        return Response({"post": "create"}, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        return Response({"get": "list"}, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        return Response({"get": "retrieve"}, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        return Response({"put": "update"}, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        return Response({"put": "partial_update"}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        return Response({"delete": "destroy"}, status=status.HTTP_204_NO_CONTENT)


# -------------------------------------------------------------------------------------------------
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins


class HeroGenericViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                         mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                         mixins.CreateModelMixin,
                         GenericViewSet):
    """GenericViewSet 结合 mixins"""
    queryset = HeroInfo.objects.all()
    serializer_class = HeroInfoSerializer


# -------------------------------------------------------------------------------------------------
from rest_framework.viewsets import ModelViewSet


class HeroModelViewSet(ModelViewSet):
    queryset = HeroInfo.objects.all()
    serializer_class = HeroInfoSerializer


# -------------------------------------------------------------------------------------------------

from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action


class BookInfoViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, GenericViewSet):
    queryset = BookInfo.objects.all()
    serializer_class = BookInfoSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            # return OrderCommitSerializer
            pass
        else:
            # return OrderDataSerializer
            pass

    def latest(self, request):
        """
        返回最新的图书信息
        """
        book = BookInfo.objects.latest('id')
        serializer = self.get_serializer(book)
        return Response(serializer.data)

    def read(self, request, pk):
        """
        修改图书的阅读量数据
        """
        book = self.get_object()
        book.bread = request.data.get('read')
        book.save()
        serializer = self.get_serializer(book)
        return Response(serializer.data)


"""
urlpatterns = [
    url(r'^books/$', views.BookInfoViewSet.as_view({'get': 'list'})),
    url(r'^books/latest/$', views.BookInfoViewSet.as_view({'get': 'latest'})),
    url(r'^books/(?P<pk>\d+)/$', views.BookInfoViewSet.as_view({'get': 'retrieve'})),
    url(r'^books/(?P<pk>\d+)/read/$', views.BookInfoViewSet.as_view({'put': 'read'})),
]
"""



