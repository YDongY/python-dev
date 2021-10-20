from rest_framework.viewsets import ModelViewSet
from .serializers import BookInfoSerializer
from booktest.models import BookInfo


class BookInfoViewSet(ModelViewSet):
    queryset = BookInfo.objects.all()  # 指明该视图集在查询数据时使用的查询集
    serializer_class = BookInfoSerializer  # 指明该视图在进行序列化或反序列化时使用的序列化器
