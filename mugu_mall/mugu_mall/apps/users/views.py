from django.shortcuts import render

# Create your views here.

# 在注册的时候判断用户名是否存在
from rest_framework import status
from rest_framework.generics import CreateAPIView, GenericAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from users import serializers
from users.models import User
from users.serializers import UserSerializer, EmailSerializer, UserDetailSerializer


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




class UserDetailView(RetrieveAPIView):
    """
    用户详情
    """
    serializer_class = serializers.UserDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

# class UserDetailView(GenericAPIView,RetrieveModelMixin):
#     """
#     用户详情
#     """
#     serializer_class = UserDetailSerializer
#     permission_classes = [IsAuthenticated]
#
#     def get_object(self):
#         return self.request.user
#
#     def get(self,request):
#         # user = request.user
#         # serializer = UserDetailSerializer(user)
#
#         # serializer = self.get_serializer(user)
#
#
#         return self.retrieve(request)

class EmailView(UpdateAPIView):
    """
    用户设置邮箱
    """
    permission_classes = [IsAuthenticated]
    serializer_class = EmailSerializer
    def get_object(self):
        return self.request.user

    # 如果继承了RetrieveAPIView,下面的方法就不需要在写了，但是GenericAPIView的get_object方法默认根据用户的主键pk查询数据，我们可以重写此方法
    # def put(self,request):
    #     # user = request.user
    #     # serializer = EmailSerializer(user,data=request.data)
    #     # serializer = self.get_serializer(user,data=request.data)
    #     # serializer.is_valid()
    #     # serializer.save()
    #
    #     return self.retrieve(request)

class VerifyEmailView(APIView):
    """
    邮箱验证
    """
    def put(self, request):
        # 获取token
        token = request.query_params.get('token')
        if not token:
            return Response({'message': '缺少token'}, status=status.HTTP_400_BAD_REQUEST)

        # 验证token
        user = User.check_verify_email_token(token)
        if user is None:
            return Response({'message': '链接信息无效'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            user.email_active = True
            user.save()
            return Response({'message': 'OK'})























