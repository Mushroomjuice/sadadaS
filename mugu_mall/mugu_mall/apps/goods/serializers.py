from rest_framework import serializers
# from drf_haystack.serializers import HaystackSerializer

from goods.models import SKU
# from goods.search_indexes import SKUIndex
from goods.search_indexes import SKUIndex


class SKUSerializer(serializers.ModelSerializer):
    """商品序列化器类"""
    class Meta:
        model = SKU
        fields = ('id', 'name', 'price', 'default_image_url', 'comments')


# class SKUIndexSerializer(HaystackSerializer):
#     """搜索结果序列化器类"""
#     object = SKUSerializer(label='商品')
#
#     class Meta:
#         # 指定索引类
#         index_classes = [SKUIndex]
#         fields = ('text', 'object')

from drf_haystack.serializers import HaystackSerializer



class SKUIndexSerializer(HaystackSerializer):
    """
    SKU索引结果数据序列化器
    """
    object = SKUSerializer(read_only=True)

    class Meta:
        index_classes = [SKUIndex]
        fields = ('text', 'object')