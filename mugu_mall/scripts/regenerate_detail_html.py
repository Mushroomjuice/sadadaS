#! /usr/bin/env python

# 批量生成所有商品的静态详情页面
import sys
sys.path.insert(0, '../')

# 设置Django运行所依赖的环境变量
import os
if not os.environ.get("DJANGO_SETTINGS_MODULE"):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mugu_mall.settings.dev")

# 让Django进行一次初始化
import django
django.setup()

from django.conf import settings

from goods.models import SKU
from goods.utils import get_categories


def generate_static_sku_detail_html(sku_id):
    """生成指定商品的静态详情页面"""
    # 1. 获取商品详情页所需数据
    # 商品分类菜单
    categories = get_categories()

    # 获取当前sku的信息
    sku = SKU.objects.get(id=sku_id)
    sku.images = sku.skuimage_set.all()

    # 面包屑导航信息中的频道
    goods = sku.goods
    goods.channel = goods.category1.goodschannel_set.all()[0]

    # 构建当前商品的规格键
    # sku_key = [规格1参数id， 规格2参数id， 规格3参数id, ...]
    sku_specs = sku.skuspecification_set.order_by('spec_id')
    sku_key = []
    for spec in sku_specs:
        sku_key.append(spec.option.id)

    # 获取当前商品的所有SKU
    skus = goods.sku_set.all()

    # 构建不同规格参数（选项）的sku字典
    # spec_sku_map = {
    #     (规格1参数id, 规格2参数id, 规格3参数id, ...): sku_id,
    #     (规格1参数id, 规格2参数id, 规格3参数id, ...): sku_id,
    #     ...
    # }
    spec_sku_map = {}
    for s in skus:
        # 获取sku的规格参数
        s_specs = s.skuspecification_set.order_by('spec_id')
        # 用于形成规格参数-sku字典的键
        key = []
        for spec in s_specs:
            key.append(spec.option.id)
        # 向规格参数-sku字典添加记录
        spec_sku_map[tuple(key)] = s.id

    # 获取当前商品的规格信息
    # specs = [
    #    {
    #        'name': '屏幕尺寸',
    #        'options': [
    #            {'value': '13.3寸', 'sku_id': xxx},
    #            {'value': '15.4寸', 'sku_id': xxx},
    #        ]
    #    },
    #    {
    #        'name': '颜色',
    #        'options': [
    #            {'value': '银色', 'sku_id': xxx},
    #            {'value': '黑色', 'sku_id': xxx}
    #        ]
    #    },
    #    ...
    # ]
    specs = goods.goodsspecification_set.order_by('id')
    # 若当前sku的规格信息不完整，则不再继续
    if len(sku_key) < len(specs):
        return
    for index, spec in enumerate(specs):
        # 复制当前sku的规格键
        key = sku_key[:]
        # 该规格的选项
        options = spec.specificationoption_set.all()
        for option in options:
            # 在规格参数sku字典中查找符合当前规格的sku
            key[index] = option.id
            option.sku_id = spec_sku_map.get(tuple(key))

        spec.options = options

    # 2. 调用`detail.html`模板文件，进行模板渲染，获取渲染之后的html内容
    context = {
        'categories': categories,
        'goods': goods,
        'specs': specs,
        'sku': sku
    }

    # 加载模板
    from django.template import loader
    temp = loader.get_template('detail.html')

    # 模板渲染
    res_html = temp.render(context)

    # 3. 将渲染之后的html内容保存成静态文件(商品详情页的静态文件保存时可以以商品id作为文件名称)
    save_path = os.path.join(settings.GENERATED_STATIC_HTML_FILES_DIR, 'goods/%s.html' % sku_id)

    with open(save_path, 'w') as f:
        f.write(res_html)


if __name__ == "__main__":
    # 获取所有的商品
    skus = SKU.objects.all()

    # 遍历生成每个商品的静态详情页面
    for sku in skus:
        generate_static_sku_detail_html(sku.id)
