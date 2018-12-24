from django.shortcuts import render

# Create your views here.
# GET /categories/(?P<category_id>\d+)/skus/?page=<页码>&page_size=<页容量>&ordering=<排序字段>
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView

from goods.models import SKU
from goods.serializers import SKUSerializer, SKUIndexSerializer


class SKUListView(ListAPIView):
    # 指定视图所使用的序列化器类
    serializer_class = SKUSerializer
    # queryset = SKU.objects.filter(category_id=category_id)

    def get_queryset(self):
        """返回当前视图所使用的查询集"""
        category_id = self.kwargs['category_id']
        return SKU.objects.filter(category_id=category_id)

    # 排序
    filter_backends = [OrderingFilter]
    # 指定排序字段
    ordering_fields = ('create_time', 'price', 'sales')

    # def get(self, request, category_id):
    #     """
    #     self.kwargs: 字典，保存从url地址中提取的所有命名参数
    #     获取分类下面SKU商品的列表数据:
    #     1. 根据`category_id`获取分类对应SKU商品的数据
    #     2. 将SKU商品的数据序列化并返回
    #     """
    #     # 1. 根据`category_id`获取分类对应SKU商品的数据
    #     skus = self.get_queryset()


from drf_haystack.viewsets import HaystackViewSet

class SKUSearchViewSet(HaystackViewSet):
    """
    SKU搜索
    """
    index_models = [SKU]

    serializer_class = SKUIndexSerializer