import random
from django.shortcuts import render
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from celery_tasks.sms.tasks import send_sms_code

from verifications import constants
from mugu_mall.libs.yuntongxun.sms import CCP

# Create your views here.
# 获取logger
import logging
logger = logging.getLogger('django')


# GET /sms_codes/(?P<mobile>1[3-9]\d{9})/
class SMSCodeView(APIView):
    def get(self, request, mobile):
        """
        获取短信验证码:
        1. 随机生成6位数字作为短信验证码
        2. 在redis中存储短信验证码内容，以`mobile`为key，以短信验证码的内容为value
        3. 使用云通讯给`mobile`发送短信验证码
        4. 返回应答，发送短信成功
        """
        # 获取redis链接
        redis_conn = get_redis_connection('verify_codes')
        # 判断60s之内是否给`mobile`发送过短信
        send_flag = redis_conn.get('send_flag_%s' % mobile) # None

        if send_flag:
            return Response({'message': '发送短信过于频繁'}, status=status.HTTP_400_BAD_REQUEST)

        # 1. 随机生成6位数字作为短信验证码
        sms_code = '%06d' % random.randint(0, 999999) # 000010

        # 2. 在redis中存储短信验证码内容，以`mobile`为key，以短信验证码的内容为value
        # redis管道：可以向管道中添加多个redis命令，然后一次性执行
        # 创建redis管道对象
        pl = redis_conn.pipeline()

        # redis_conn.set('<key>', '<value>', '<expries>')
        # redis_conn.setex('<key>', '<expires>', '<value>')
        # 向redis管道中添加命令
        pl.setex('sms_%s' % mobile, constants.SMS_CODES_REDIS_EXPIRES, sms_code)
        # 保存给`mobile`手机号发送短信标记
        pl.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)

        # 一次性执行管道中的命令
        pl.execute()

        # 3. 使用云通讯给`mobile`发送短信验证码
        expires = constants.SMS_CODES_REDIS_EXPIRES // 60
        # try:
        #     res = CCP().send_template_sms(mobile, [sms_code, expires], constants.SMS_CODE_TEMP_ID)
        # except Exception as e:
        #     logger.error('发送短信异常')
        #     return Response({'message': '发送短信异常'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        #
        # if res != 0:s.SMS_CODES_REDIS_EXPIRES, sms_code)
        # 保存给`mobile`手机号发送短信标记
        #     # 发送短信失败
        #     logger.error('发送短信失败')
        #     return Response({'message': '发送短信失败'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # 4. 返回应答，发送短信成功
        send_sms_code.delay(mobile, sms_code, expires)
        return Response({'message': 'OK'})
