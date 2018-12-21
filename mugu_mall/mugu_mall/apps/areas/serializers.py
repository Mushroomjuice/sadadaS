from rest_framework import serializers

from areas.models import Area


class AreaSerializer(serializers.ModelSerializer):
    """
    地区序列化器
    """
    class Meta:
        model = Area
        fields = ('id','name')

class SubAreaSerializer(serializers.ModelSerializer):
    """
    指定区域的序列化器
    """
    subs = AreaSerializer(label='下级区域',many=True)
    class Meta:
        model = Area
        fields = ('id','name','subs')
