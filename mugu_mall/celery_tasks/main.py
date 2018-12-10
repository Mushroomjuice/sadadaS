from celery import Celery

# 创建一个Celery类的对象
celery_app = Celery('celery_tasks')

# 加载配置
celery_app.config_from_object('celery_tasks.config')

# 让worker启动时自动发现任务函数
celery_app.autodiscover_tasks(['celery_tasks.sms'])