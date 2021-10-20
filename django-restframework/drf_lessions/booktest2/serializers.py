from rest_framework import serializers

from booktest.models import BookInfo


class BookInfoSerializer(serializers.ModelSerializer):
    """图书数据序列化器"""

    class Meta:
        model = BookInfo  # 指明序列化的模型
        fields = '__all__'  # 指明序列化哪些字段，'__all__' 表示所有字段
