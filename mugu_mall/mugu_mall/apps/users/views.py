from django.shortcuts import render
from rest_framework.authentication import BaseAuthentication
# Create your views here.
from rest_framework.permissions import IsAuthenticated
# 在注册的时候判断用户名是否存在
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView, GenericAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.mixins import RetrieveModelMixin, CreateModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from goods.serializers import SKUSerializer
from goods.models import SKU
from users import serializers, constants
from users.models import User
from users.serializers import UserSerializer, EmailSerializer, UserDetailSerializer, AddressTitleSerializer, \
    UserAddressSerializer, HistorySerializer


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


# POST /addresses/
class AddressViewSet(CreateModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = UserAddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.addresses.filter(is_deleted=False)

    # GET /addresses/
    def list(self, request, *args, **kwargs):
        """
        用户地址列表数据
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        user = request.user
        return Response({
            'user_id': user.id,
            'default_address_id': user.default_address_id,
            'limit': constants.USER_ADDRESS_COUNTS_LIMIT,
            'addresses': serializer.data,
        })

    def create(self, request, *args, **kwargs):
        """
        地址的新增:
        0. 判断用户的地址数量是否超过上限
        1. 获取参数并进行校验
        2. 创建并保存用户的地址信息
        3. 返回应答
        """
        # 0. 判断用户的地址数量是否超过上限
        user = request.user
        # 获取登录用户地址数量
        count = user.addresses.filter(is_deleted=False).count()

        if count > constants.USER_ADDRESS_COUNTS_LIMIT:
            return Response({'message': '地址数量超过上限'}, status=status.HTTP_400_BAD_REQUEST)

        return super().create(request)

        # # 1. 获取参数并进行校验
        # serializer = self.get_serializer(data=request.data)
        # serializer.is_valid(raise_exception=True)
        #
        # # 2. 创建并保存用户的地址信息(create)
        # serializer.save()
        #
        # # 3. 返回应答
        # return Response(serializer.data, status=status.HTTP_201_CREATED)

    # delete /addresses/<pk>/
    def destroy(self, request, *args, **kwargs):
        """
        处理删除
        """
        address = self.get_object()

        # 进行逻辑删除
        address.is_deleted = True
        address.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    # put /addresses/pk/status/
    @action(methods=['put'], detail=True)
    def status(self, request, pk=None):
        """
        设置默认地址
        """
        # 从用户的地址中根据pk获取对应地址
        address = self.get_object()
        # 将当前地址设置为用户的默认地址
        request.user.default_address = address
        request.user.save()
        return Response({'message': 'OK'}, status=status.HTTP_200_OK)

    # put /addresses/pk/title/
    # 需要请求体参数 title
    @action(methods=['put'], detail=True)
    def title(self, request, pk=None):
        """
        修改标题
        """
        # 从用户的地址中根据pk获取对应地址
        address = self.get_object()
        # 获取title并进行校验
        serializer = AddressTitleSerializer(instance=address, data=request.data)
        serializer.is_valid(raise_exception=True)
        # 设置用户地址的标题
        serializer.save()
        return Response(serializer.data)

# POST /browse_histories/
class BrowseHistoryView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = HistorySerializer

    # def post(self, request):
    #     """
    #     浏览记录的添加:
    #     1. 获取sku_id并进行校验(sku_id必传，sku_id对应的商品是否存在)
    #     2. 在redis中保存登录用户的浏览商品的记录
    #     3. 返回应答
    #     """
    #     # 1. 获取sku_id并进行校验(sku_id必传，sku_id对应的商品是否存在)
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #
    #     # 2. 在redis中保存登录用户的浏览商品的记录(create)
    #     serializer.save()
    #
    #     # 3. 返回应答
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request):
        """
        获取用户的浏览记录:
        1. 从redis中获取用户浏览的商品的sku_id
        2. 根据商品的sku_id获取对应商品的信息
        3. 将商品的数据序列化并返回
        """
        # 获取登录用户
        user = request.user

        # 获取redis链接对象
        redis_conn = get_redis_connection('histories')
        history_key = 'history_%s' % user.id

        # 1. 从redis中获取用户浏览的商品的sku_id
        # [b'<sku_id>', b'<sku_id>', ...]
        sku_ids = redis_conn.lrange(history_key, 0, -1)

        # 2. 根据商品的sku_id获取对应商品的信息
        skus = []
        for sku_id in sku_ids:
            sku = SKU.objects.get(id=sku_id)
            skus.append(sku)

        # 3. 将商品的数据序列化并返回
        serializer = SKUSerializer(skus, many=True)
        return Response(serializer.data)
















