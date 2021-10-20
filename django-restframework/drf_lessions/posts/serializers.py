from django.contrib.auth.models import User
from rest_framework import serializers
from django.utils import timezone
from .models import Post, Tag


def isnumeric(value):
    if str(value).isnumeric():
        raise serializers.ValidationError("密码不能是纯数字")
    return value


class IsNumeric(object):
    def __init__(self):
        """可以接收参数"""
        pass

    def __call__(self, value):
        if str(value).isnumeric():
            raise serializers.ValidationError("密码不能是纯数字")
        return value


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(label='用户名', required=True)
    password = serializers.CharField(label='密码', write_only=True, validators=[isnumeric])
    email = serializers.CharField(label='邮箱', allow_blank=True, required=False)

    # 因为 post_set 是 User 模型上的反向关系，默认不会被包含，所以需要显式的为它添加一个字段。
    # post_set = serializers.PrimaryKeyRelatedField(many=True, queryset=Post.objects.all())
    # post_set = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    # post_set = serializers.StringRelatedField(many=True)
    # post_set = serializers.HyperlinkedRelatedField(view_name='posts:rest-post-detail', lookup_field='pk', many=True,
    #                                               read_only=True)

    # post_set = serializers.SlugRelatedField(read_only=True, slug_field='content', many=True)

    #
    post_set = serializers.HyperlinkedIdentityField(view_name='posts:rest-post-detail', lookup_field='pk', many=True)

    # snippets = serializers.HyperlinkedRelatedField(many=True, view_name='snippet-detail', read_only=True)
    def validate_username(self, value):
        user = User.objects.filter(username=value).first()
        if user:
            raise serializers.ValidationError("用户名已存在")
        return value

    def validate_password(self, value):
        """单个字段验证，validate_<field_name>"""
        if len(value) < 6 or len(value) > 20:
            raise serializers.ValidationError("需要6-20个字符的密码")
        return value

    def validate(self, attrs):
        return attrs

    def create(self, validated_data):
        """ 创建用户 """
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.set_password(validated_data.get('password', instance.password))
        instance.save()

        return instance

    def save(self, **kwargs):
        """
        覆盖 save() 方法，在使用 serializer.save() 时不调用 create 或 update 方法一般用于不保存对象，而是做其他的事
        """
        pass


class AuthorField(serializers.RelatedField):
    """自定义关系字段，继承自 RelatedField 实现 to_representation 方法"""

    def to_representation(self, value):
        """模型实例"""
        return f'{value.username}-{value.email}'


from rest_framework.reverse import reverse


class AuthorHyperlink(serializers.HyperlinkedRelatedField):
    view_name = 'posts:rest-user-detail'
    queryset = User.objects.all()

    def get_url(self, obj, view_name, request, format):
        # /users/<pk>/
        url_kwargs = {
            'pk': obj.pk
        }
        return reverse(view_name, kwargs=url_kwargs, request=request, format=format)

    def get_object(self, view_name, view_args, view_kwargs):
        lookup_kwargs = {
            'pk': view_kwargs['pk']
        }
        return self.get_queryset().get(**lookup_kwargs)


class PostSerializer(serializers.ModelSerializer):
    # 1. 默认是将关联模型的 id 序列化
    # author = serializers.PrimaryKeyRelatedField(label='作者', read_only=True)
    # author = serializers.PrimaryKeyRelatedField(label='作者', queryset=User.objects.all())

    # 2. 通过  source 可以修改显示外键属性值
    # author = serializers.ReadOnlyField(source='author.username')

    # 3. 显示外键属性值为外键模型的 __str__ 方法返回值
    # author = serializers.StringRelatedField()

    # 4. 通过 UserSerializer 显示外键属性值
    # author = UserSerializer(read_only=True)

    # 5. 通过设置 Meta depth 属性可嵌套表示外键属性所有字段

    # 6. 显示外键连接，但是在创建序列化对象时需要传递 context={'request': request}
    # author = serializers.HyperlinkedRelatedField(read_only=True, view_name='posts:rest-user-detail')

    # 7. 指定外键属性值，但是需要该字段具有 unique=True
    # author = serializers.SlugRelatedField(read_only=True, slug_field='username')

    # 8. 超链接身份字段
    # author = serializers.HyperlinkedIdentityField(view_name='posts:rest-user-detail')

    # 9. 自定义关系字段
    # author = AuthorField(queryset=User.objects.all())
    # author = AuthorField(read_only=True)

    # 10. 自定义超链接字段
    author = AuthorHyperlink()

    # 额外字段，source 调用 get_absolute_url 方法
    url = serializers.URLField(source='get_absolute_url', allow_blank=True, allow_null=True)

    # validators 验证器
    title = serializers.CharField(validators=[])

    # style 控制渲染器如何渲染字段
    status = serializers.ChoiceField(choices=['draft', 'published'], style={'base_template': 'radio.html'})

    # initial 填充表单默认值
    create_time = serializers.DateTimeField(initial=timezone.datetime.now)

    # 序列化方法字段，是一个只读字段
    tag_set = serializers.SerializerMethodField()

    def get_tag_set(self, obj):
        """默认为get_< field_name > , obj 为 模型实例"""
        data = []
        tags = obj.tag_set.all()
        for tag in tags:
            data.append(tag.name)

        return data

    class Meta:
        model = Post  # 指定序列化模型
        # fields = '__all__' # 显示所有字段
        fields = ['id', 'title', 'content', 'status', 'author', 'create_time', 'update_time', 'url',
                  'tag_set']  # 显示指定字段，可包含反向关系
        # exclude = ['slug']  # 排除显示某些字段
        read_only_fields = ['id']  # 指定只读字段，editable=False 和 AutoField 模型字段默认只读，不需要添加
        # depth = 1  # 嵌套表示外键属性所有字段

    def create(self, validated_data):
        """通过 save(author=...) 传递额外参数，保存的时候，将 author 设置为当前登录的用户"""
        # return Post.objects.create(**validated_data)

        # 2. 也可以通过创建序列化器对象时传递的 context={'request': request} 获取登录用户
        user = self.context['request'].user
        validated_data['author'] = user
        return Post.objects.create(**validated_data)


class TagListSerializer(serializers.ListSerializer):
    @classmethod
    def many_init(cls, *args, **kwargs):
        # Instantiate the child serializer.
        kwargs['child'] = cls()
        # Instantiate the parent list serializer.
        return TagListSerializer(*args, **kwargs)

    def create(self, validated_data):
        """自定义多重创建"""
        tags = [Tag(**item) for item in validated_data]
        return Tag.objects.bulk_create(tags)


class TagSerializer(serializers.HyperlinkedModelSerializer):
    """
        默认情况下，HyperlinkedModelSerializer 将包含一个 url 字段而不是主键字段，可以使用该 URL_FIELD_NAME 设置全局覆盖此设置
        且在创建序列化器时，需要传递 context 参数：
            - context={'request': request} 则生成的是 绝对 URL
            - context={'request': None} 则生成的是 相对 URL
    """

    # 显示设置
    posts = serializers.HyperlinkedRelatedField(view_name='posts:rest-post-detail', lookup_field='pk', many=True,
                                                read_only=True)

    class Meta:
        model = Tag
        fields = ['url', 'id', 'name', 'posts']
        extra_kwargs = {
            'url': {'view_name': 'posts:rest-tag-detail', 'lookup_field': 'pk'},
            # 'posts': {'view_name': 'posts:post-detail', 'lookup_field': 'pk'}
        }

        # 自定义 ListSerializer 行为
        # list_serializer_class = TagListSerializer


class TagReadOnlySerializer(serializers.BaseSerializer):
    """只读 BaseSerializer 类，继承自 BaseSerializer 实现 .to_representation()方法"""

    def to_representation(self, instance):
        return {
            'id': instance.id,
            'name': instance.name
        }


class TagReadWriteSerializer(serializers.BaseSerializer):
    """
        读写 BaseSerializer 类，继承自 BaseSerializer 实现一个.to_internal_value()方法

    """

    def to_internal_value(self, data):
        name = data.get('name')
        if not name:
            raise serializers.ValidationError({
                'score': 'This field is required.'
            })

        # 返回经过验证的值，设置给 .validated_data 属性
        return {
            'name': name
        }
