from django.shortcuts import render

# Create your views here.
from rest_framework.generics import GenericAPIView, ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_extensions.cache.mixins import CacheResponseMixin

from areas.models import Area
from areas.serializers import AreaSerializer, SubAreaSerializer


class AreasView(ListAPIView):
    """
    获取所有省的信息
    """
    queryset = Area.objects.filter(parent=None)
    serializer_class = AreaSerializer
    # def get(self,request):
    #     # areas = Area.objects.filter(parent=None)
    #     # serializer = AreaSerializer(areas,many=True)
    #     serializer = self.get_serializer(self.queryset.all(),many=True)
    #     return Response(serializer.data)

class SubAreasView(RetrieveAPIView):
    """"
    获取制定区域的信息
    """
    queryset = Area.objects.all()
    serializer_class = SubAreaSerializer
    # def get(self,request,pk):
    #     area = self.get_object()
    #     serializer = self.get_serializer(area)
    #     return Response(serializer.data)


"""
上面两个视图可以使用视图集，配合router,实现自动路由实现
"""

class AreaViewSet(CacheResponseMixin, ReadOnlyModelViewSet):
    """
    因为视图集包含了不同的视图，使用的序列化器和查询集不同，所以通常都需要我们自己重写GenericAPIView的方法
    使用drf的缓存扩展实现数据在redis中的缓存
    """
    def get_serializer_class(self):
        if self.action == 'list':
            return AreaSerializer
        else:
            return SubAreaSerializer

    def get_queryset(self):
        if self.action == 'list':
            return Area.objects.filter(parent=None)
        else:
            return Area.objects.all()








