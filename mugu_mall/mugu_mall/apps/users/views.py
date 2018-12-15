from django.shortcuts import render

# Create your views here.

# 在注册的时候判断用户名是否存在
from rest_framework.generics import CreateAPIView, GenericAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from users import serializers
from users.models import User
from users.serializers import UserSerializer


class UsernameCountView(APIView):
    """
    用户名数量
    """
    def get(self,request,username):
        """
        获取制定用户名数量，如果为0表示该用户名没有被注册
        :param request:
        :param username:
        :return:
        """
        count = User.objects.filter(username = username).count()
        data = {
            'username':username,
            'count':count
        }
        return Response(data)

# 判断手机号是否存在
class MobilecountView(APIView):
    """
    手机号数量

    """
    def get(self,request,mobile):
        count = User.objects.filter(mobile = mobile).count()
        data = {
            'mobile':mobile,
            'count':count
        }
        return Response(data)

# 注册
class UserView(CreateAPIView):
    # serializer_class = UserSerializer
    """
    获取参数
    校验参数
    创建用户模型并返回

    """
    serializer_class = UserSerializer
    # 获取参数 用户名 密码 手机号 验证码 是否统一协议
    # def post(self,request):
        # 指定序列化器,创建序列化对象
        # serizlizer = UserSerializer(data=request.data)
        # serizlizer.is_valid()
        # print(serizlizer.errors)
        # print(serizlizer.validated_data)
        # serizlizer.save()

        # return Response(serizlizer.data)

        # 当继承GenericAPIView
        # serializer = self.get_serializer(data=request.data)
        # serializer.is_valid()
        # serializer.save()
        # return Response(serializer.data)


from rest_framework.permissions import IsAuthenticated

class UserDetailView(RetrieveAPIView):
    """
    用户详情
    """
    serializer_class = serializers.UserDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

