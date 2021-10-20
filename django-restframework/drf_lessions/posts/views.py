# --------------------------------- 基于函数视图 ----------------------------------
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from .serializers import UserSerializer

from django.contrib.auth.models import User


@csrf_exempt
def user_list(request):
    """
    显示所有用户，或创建新用户
    """
    if request.method == 'GET':
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)


@csrf_exempt
def user_detail(request, pk):
    """
    获取、更新、删除一个用户
    """
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = UserSerializer(user)
        return JsonResponse(serializer.data)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = UserSerializer(user, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        user.delete()
        return HttpResponse(status=204)


# --------------------------------- 基于 REST framework 函数视图 ----------------------------------
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer


@api_view(['GET', 'POST'])
def rest_user_list(request):
    """
    显示所有用户，或创建新用户
    """
    if request.method == 'GET':
        users = User.objects.all()
        serializer = UserSerializer(users, many=True, context={"request": request})
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def rest_user_detail(request, pk):
    """
    获取、更新、删除一个用户
    """
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# --------------------------------- 基于 REST framework 类视图 ----------------------------------
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import PostSerializer
from .models import Post


class PostList(APIView):
    """
    获取所有文章、或创建新文章
    """

    def get(self, request, format=None):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            # 在保存文章的时候传递额外参数给 create 方法
            serializer.save(author=self.request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostDetail(APIView):
    """
    获取、更新、删除一篇文章
    """

    def get_object(self, pk):
        try:
            return Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        snippet = self.get_object(pk)
        serializer = PostSerializer(snippet, context={'request': request})
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        snippet = self.get_object(pk)
        serializer = PostSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        snippet = self.get_object(pk)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


"""------------------------------------------------ 基于 REST framework mixin 组合视图 -------------------------------------------------------"""
from rest_framework import mixins
from rest_framework import generics

from .models import Tag
from .serializers import TagSerializer


class TagList(mixins.ListModelMixin,
              mixins.CreateModelMixin,
              generics.GenericAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class TagDetail(mixins.RetrieveModelMixin,
                mixins.UpdateModelMixin,
                mixins.DestroyModelMixin,
                generics.GenericAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


"""------------------------------------------------ 基于 REST framework 通用类视图 -------------------------------------------------------"""

from rest_framework import generics
from .serializers import TagSerializer
from .models import Tag


class TagGenericsList(generics.ListCreateAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class TagGenericsDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


"""------------------------------------------------ 自定义 Mixin -------------------------------------------------------"""

from rest_framework.generics import get_object_or_404


class MultipleFieldLookupMixin:
    """根据 URL conf 中的多个字段查找对象"""

    def get_object(self):
        queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset)
        filter = {}
        for field in self.lookup_fields:
            if self.kwargs[field]:  # Ignore empty fields.
                filter[field] = self.kwargs[field]
        obj = get_object_or_404(queryset, **filter)  # Lookup the object
        self.check_object_permissions(self.request, obj)
        return obj


class RetrieveUserView(MultipleFieldLookupMixin, generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_fields = ['pk', 'username']


"""------------------------------------------------ 基于 REST framework 视图集 -------------------------------------------------------"""
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.renderers import AdminRenderer
from .serializers import UserSerializer


class UserViewSet(viewsets.ViewSet):
    """
    获取单个用户和所有用户的视图集
    """

    renderer_classes = [AdminRenderer]

    def list(self, request):
        queryset = User.objects.all()
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = User.objects.all()
        user = get_object_or_404(queryset, pk=pk)
        serializer = UserSerializer(user)
        return Response(serializer.data)


"""------------------------------------------------ 基于 REST framework 视图集 -------------------------------------------------------"""
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer, TemplateHTMLRenderer

from .serializers import UserSerializer


class UserModelViewSet(viewsets.ModelViewSet):
    """
    包含用户所有操作的视图集
    """
    serializer_class = UserSerializer
    queryset = User.objects.all()

    parser_classes = [JSONParser, FormParser]
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer, TemplateHTMLRenderer]

    # @action(detail=True, methods=['put'], permission_classes=[IsAdminOrIsSelf])
    @action(detail=True, methods=['put', 'get'])
    def password(self, request, pk=None):
        """添加修改密码的 action"""
        user = self.get_object()
        if not user:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'PUT':
            user.set_password(request.data.get('password'))
            user.save()
            return Response({'status': 'password set'})
        else:
            return Response({'password': user.password})

    @password.mapping.delete  # 相当于给 password action 添加一个 HTTP delete 操作
    def delete_password(self, request, pk=None):
        """Delete the user's password."""
        user = self.get_object()
        if not user:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        # 这里删除密码设置为默认密码
        user.set_password('admin')
        user.save()
        return Response({'status': 'password delete'})

    @action(detail=False)
    def recent_users(self, request):
        """获取最近活动的用户 action"""
        recent_users = User.objects.all().order_by('-last_login')

        page = self.paginate_queryset(recent_users)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(recent_users, many=True)
        return Response(serializer.data)

    @action(detail=True)
    def set_password_url(self, request, pk=None):
        # 反向解析，自动添加 basename 路由名称的前缀
        return Response({"set_password_url": self.reverse_action('password', args=pk)})


# --------------------------------------- TemplateHTMLRenderer ----------------------------------
from rest_framework.authentication import BaseAuthentication, TokenAuthentication
from rest_framework import exceptions


class CustomBasicAuthentication(BaseAuthentication):
    def authenticate(self, request):
        """
            return:
                - None 则不认证
                - (user,auth) 身份验证成功

            认证失败 raise exceptions.AuthenticationFailed
        """
        username = request.META.get('HTTP_X_USERNAME')
        if not username:
            return None
            # raise exceptions.AuthenticationFailed('No such user')
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('No such user')

        return user, None

    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response, or `None` if the
        authentication scheme should return `403 Permission Denied` responses.
        """
        return 'Basic realm="api"'


from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        # if request.method in permissions.SAFE_METHODS:
        #     return True

        # Instance must have an attribute named `owner`.
        return obj == request.user


from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie, vary_on_headers
from rest_framework.throttling import UserRateThrottle
from django_filters.rest_framework import DjangoFilterBackend


class UserDetailTemplateHTMLRenderer(generics.RetrieveAPIView):
    """
    A view that returns a templated HTML representation of a given user.
    """

    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsOwnerOrReadOnly]
    authentication_classes = []
    permission_classes = []

    queryset = User.objects.all()

    # renderer_classes = [TemplateHTMLRenderer]
    renderer_classes = []

    throttle_classes = [UserRateThrottle]

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['id', 'username']

    serializer_class = UserSerializer

    # With auth: cache requested url for each user for 2 hours
    # @method_decorator(cache_page(60 * 60 * 2))
    # @method_decorator(vary_on_headers("Authorization", ))
    # def get(self, request, *args, **kwargs):
    #     self.object = self.get_object()
    #     return Response({'user': self.object}, template_name='user_detail.html')


from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 2
    page_size_query_param = 'page_size'
    max_page_size = 5


# -------------------------------------------------------------------------------------------
from rest_framework.authentication import BasicAuthentication, SessionAuthentication, TokenAuthentication, \
    RemoteUserAuthentication
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.throttling import AnonRateThrottle

from django.core.cache import caches


# class CustomAnonRateThrottle(AnonRateThrottle):
#     cache = caches['default']


import random
from rest_framework import throttling


class RandomRateThrottle(throttling.BaseThrottle):
    """将在每 10 个请求中随机限制 1 个"""

    def allow_request(self, request, view):
        return random.randint(1, 10) != 1

    def wait(self):
        return 10


class UserList(generics.ListAPIView):
    # authentication_classes = [SessionAuthentication]
    # permission_classes = []

    # renderer_classes = [JSONRenderer, BrowsableAPIRenderer]
    throttle_classes = [RandomRateThrottle]
    # filter_backends = [DjangoFilterBackend]
    # filter_fields = ['id', 'username']
    # search_fields = ['username', 'email']
    # ordering_fields = ['id', 'username']
    # ordering = ['id']

    # pagination_class = PageNumberPagination

    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get(self, request, *args, **kwargs):
        print(self.request.user)
        print(self.request.auth)
        return self.list(request, *args, **kwargs)
