from rest_framework import serializers
from booktest.models import BookInfo, HeroInfo

BOOKS = ["飞狐外传", "雪山飞狐", "连城诀", "天龙八部",
         "射雕英雄传", "白马啸西风", "鹿鼎记", "笑傲江湖",
         "书剑恩仇录", "神雕侠侣", "侠客行", "倚天屠龙记"
                                 "碧血剑", "鸳鸯刀", "越女剑"]


class BookInfoSerializer(serializers.Serializer):
    """图书数据序列化器"""
    id = serializers.IntegerField(label='ID', read_only=True)
    btitle = serializers.CharField(label='名称', max_length=20)
    bpub_date = serializers.DateField(label='发布日期')
    bread = serializers.IntegerField(label='阅读量', required=False)
    bcomment = serializers.IntegerField(label='评论量', required=False)
    image = serializers.ImageField(label='图片', required=False)

    # heroinfo_set = serializers.PrimaryKeyRelatedField(many=True)
    # heroinfo_set = HeroInfoSerializer(many=True)  # 如果一里面关联序列化多时, 需要多指定many=True

    def validate_btitle(self, value):
        """单个字段验证，validate_<field_name>"""
        if value not in BOOKS:
            raise serializers.ValidationError("该图书不是金庸的小说")
        book = BookInfo.objects.filter(btitle=value).first()
        if book:
            raise serializers.ValidationError("该图书已存在")
        return value

    def validate(self, attrs):
        """
            对多个字段进行比较验证时，可以定义 validate 方法来验证
            attr 存储的是传递过来的所有字段键值字典
        """
        return attrs

    def create(self, validated_data):
        """新建"""
        return BookInfo.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """更新，instance 为要更新的对象实例"""
        instance.btitle = validated_data.get('btitle', instance.btitle)
        instance.bpub_date = validated_data.get('bpub_date', instance.bpub_date)
        instance.bread = validated_data.get('bread', instance.bread)
        instance.bcomment = validated_data.get('bcomment', instance.bcomment)
        instance.save()
        return instance


class HeroInfoSerializer(serializers.Serializer):
    """英雄数据序列化器"""
    GENDER_CHOICES = (
        (0, 'male'),
        (1, 'female')
    )
    id = serializers.IntegerField(label='ID', read_only=True)
    hname = serializers.CharField(label='名字', max_length=20)
    hgender = serializers.ChoiceField(choices=GENDER_CHOICES, label='性别', required=False)
    hcomment = serializers.CharField(label='描述信息', max_length=200, required=False, allow_null=True)

    # 默认是将关联模型的 id 序列化
    # hbook = serializers.PrimaryKeyRelatedField(label='书籍', read_only=True)
    hbook = serializers.PrimaryKeyRelatedField(label='书籍', queryset=BookInfo.objects.all())

    # 默认是将关联模型的 __str__ 方法返回值序列化出来
    # hbook = serializers.StringRelatedField(label='书籍', read_only=True)

    # 关联模型对象的序列化器中所有字段序列化出来
    # hbook = BookInfoSerializer()

    def create(self, validated_data):
        """新建"""
        return HeroInfo.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """更新，instance 为要更新的对象实例"""
        instance.hname = validated_data.get('hname', instance.hname)
        instance.hgender = validated_data.get('hgender', instance.hgender)
        instance.hcomment = validated_data.get('hcomment', instance.hcomment)
        instance.hbook = validated_data.get('hbook', instance.hbook)
        instance.save()
        return instance


class HeroInfoModelSerializer(serializers.ModelSerializer):
    hbook = serializers.PrimaryKeyRelatedField(label='书籍', queryset=BookInfo.objects.all())

    class Meta:
        model = HeroInfo
        fields = '__all__'
        depth = 1
        read_only_fields = ('id',)
        extra_kwargs = {
            'hgender': {'required': False},
            'hcomment': {'required': False},
        }


class UserSerializer(serializers.Serializer):
    email = serializers.EmailField(help_text='字段帮助提示信息', required=True)
    username = serializers.CharField(max_length=100, allow_null=True)
    password = serializers.CharField(label='密码', write_only=True)
