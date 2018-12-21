from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from areas import views

router = DefaultRouter()
router.register(r'areas', views.AreaViewSet, base_name='areas')

urlpatterns = []

urlpatterns += router.urls
# 当使用视图集时，就不需要下面的路由定义方式了
# urlpatterns=[
#     url(r'^areas/$',views.AreasView.as_view()),
#     url(r'areas/(?P<pk>\d+)/$',views.SubAreasView.as_view()),
# ]