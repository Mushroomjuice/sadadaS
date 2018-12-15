import re

from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings

from users.models import User


# class UserSerializer(serializers.ModelSerializer):
#     """
#     创建用户的序列化器
#     """
#     password2 = serializers.CharField(label='重复密码',write_only=True)
#     sms_code = serializers.CharField(label='短信验证码',write_only=True)
#     allow = serializers.CharField(label='同意协议', write_only=True)
#
#     class Meta:
#         model = User
#         fields = ('id', 'username', 'mobile', 'password', 'password2', 'sms_code', 'allow')
#
#         extra_kwargs = {
#             'username': {
#                 'min_length': 5,
#                 'max_length': 20,
#                 'error_messages': {
#                     'min_length': '仅允许5-20个字符的用户名',
#                     'max_length': '仅允许5-20个字符的用户名',
#                 }
#             },
#             'password': {
#                 'write_only': True,
#                 'min_length': 8,
#                 'max_length': 20,
#                 'error_messages': {
#                     'min_length': '仅允许8-20个字符的密码',
#                     'max_length': '仅允许8-20个字符的密码',
#                 }
#             }
#         }
#
#         # 参数完整性，手机号是否正确，手机号是否存在，是否同意协议，两次密码是否一致，短信验证码是否正确
#         def validate_mobile(self, value):
#             # 手机号格式
#             if not re.match(r'^1[3-9]\d{9}$', value):
#                 raise serializers.ValidationError('手机号格式不正确')
#
#             # 手机号是否存在
#             count = User.objects.filter(mobile=value).count()
#
#             if count > 0:
#                 raise serializers.ValidationError('手机号已存在')
#
#             return value
#
#         def validate_allow(self, value):
#             # 是否同意协议
#             if value != 'true':
#                 raise serializers.ValidationError('请同意协议')
#
#             return value
#
#         def validate(self, attrs):
#             # 两次密码是否一致
#             password = attrs['password']
#             password2 = attrs['password2']
#
#             if password != password2:
#                 raise serializers.ValidationError('两次密码不一致')
#
#             # 短信验证码是否正确
#             # 获取真实的短信验证码
#             mobile = attrs['mobile']
#             redis_conn = get_redis_connection('verify_codes')
#
#             real_sms_code = redis_conn.get('sms_%s' % mobile)  # bytes
#
#             if real_sms_code is None:
#                 raise serializers.ValidationError('短信验证码已失效')
#
#             # 对比短信验证码
#             sms_code = attrs['sms_code']  # str
#             if real_sms_code.decode() != sms_code:
#                 raise serializers.ValidationError('短信验证码错误')
#
#             return attrs
#
#         def create(self, validated_data):
#             """
#             validated_data: 校验之后的数据
#             """
#             # 清除无用的数据
#             del validated_data['password2']
#             del validated_data['sms_code']
#             del validated_data['allow']
#
#
#             # 创建并保存新用户
#             user = User.objects.create_user(**validated_data)
#             return user


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器类"""
    password2 = serializers.CharField(label='重复密码', write_only=True)
    sms_code = serializers.CharField(label='短信验证码', write_only=True)
    allow = serializers.CharField(label='同意协议', write_only=True) # 'true'
    # token = serializers.CharField(label='JWT token', read_only=True)
    token = serializers.CharField(label='登录状态token', read_only=True)  # 增加token字段

    class Meta:
        model = User
        fields = ('id', 'username', 'mobile', 'password', 'password2', 'sms_code', 'allow','token')

        extra_kwargs = {
            'username': {
                'min_length': 5,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许5-20个字符的用户名',
                    'max_length': '仅允许5-20个字符的用户名',
                }
            },
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }
            }
        }

    # 参数完整性，手机号是否正确，手机号是否存在，是否同意协议，两次密码是否一致，短信验证码是否正确
    def validate_mobile(self, value):
        # 手机号格式
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式不正确')

        # 手机号是否存在
        count = User.objects.filter(mobile=value).count()

        if count > 0:
            raise serializers.ValidationError('手机号已存在')

        return value

    def validate_allow(self, value):
        # 是否同意协议
        if value != 'true':
            raise serializers.ValidationError('请同意协议')

        return value

    def validate(self, attrs):
        # 两次密码是否一致
        password = attrs['password']
        password2 = attrs['password2']

        if password != password2:
            raise serializers.ValidationError('两次密码不一致')

        # 短信验证码是否正确
        # 获取真实的短信验证码
        mobile = attrs['mobile']
        redis_conn = get_redis_connection('verify_codes')

        real_sms_code = redis_conn.get('sms_%s' % mobile) # bytes

        if real_sms_code is None:
            raise serializers.ValidationError('短信验证码已失效')

        # 对比短信验证码
        sms_code = attrs['sms_code'] # str
        if real_sms_code.decode() != sms_code:
            raise serializers.ValidationError('短信验证码错误')

        return attrs

    def create(self, validated_data):
        """
        validated_data: 校验之后的数据
        """
        # 清除无用的数据
        del validated_data['password2']
        del validated_data['sms_code']
        del validated_data['allow']

        # 创建并保存新用户
        user = User.objects.create_user(**validated_data)

        # # 创建并保存新用户
        # user = super().create(validated_data)
        # # 加密
        # password = validated_data['password']
        # user.set_password(password)
        # user.save()

        # # 由服务器生成一个jwt token，保存用户的身份信息
        # from rest_framework_jwt.settings import api_settings
        #
        # # 生成载荷
        # jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        # # 生成jwt token
        # jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        #
        # payload = jwt_payload_handler(user)
        # token = jwt_encode_handler(payload)
        #
        # # 给user增加属性token
        # user.token = token
        # 补充生成记录登录状态的token
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        user.token = token

        return user


class UserDetailSerializer(serializers.ModelSerializer):
    """
    用户详细信息序列化器
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'mobile', 'email', 'email_active')


class EmailSerializer(serializers.ModelSerializer):
    """
    邮箱序列化器
    """
    class Meta:
        model = User
        fields = ('id','email')
        extra_kwargs = {
            'email':{
                'required':True
            }
        }

    def update(self, instance, validated_data):
        email = validated_data['email']
        instance.email = validated_data['email']
        instance.save()

    # 增加发验证邮件功能
    # 生成验证链接
        verify_url = instance.generate_verify_email_url()
        # 发送验证邮件
        from celery_tasks.email.tasks import send_verify_email
        send_verify_email.delay(email, verify_url)
        return instance














