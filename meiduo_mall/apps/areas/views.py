from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from apps.areas.models import Area
from utils.response_code import RETCODE


class AreaView(View):
    """
    SQL 省  select * from tb_areas where parent_id is NULL;
        市  select * from tb_areas where parent_id=130000;
        县  select * from tb_areas where parent_id=130100;

    ORM 省 Area.objects.filter(parent_id=null)
        市 Area.objects.filter(parent_id=area_id)
        县 Area.objects.filter(parent_id=area_id)

    """

    def get(self, request):

        # 1.接收参数
        area_id = request.GET.get('area_id')

        from django.core.cache import cache
        if not area_id:

            # 1.获取缓存存储的 省份数据
            province_list = cache.get('province')

            if not province_list:
                print('缓存失效了')
                # 2. 省的数据 area_id 为空的
                province_model_list = Area.objects.filter(parent__isnull=True)

                # 将orm的数据对象 转换成 前端需要的json格式
                province_list = []
                for pro in province_model_list:
                    province_list.append({'id': pro.id, 'name': pro.name})

                cache.set('province', province_list, 3600)

            return JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'province_list': province_list})
        else:
            # 3. 市区的数据 area_id有值
            # 1.获取缓存存储的 省份数据
            sub_data = cache.get('subs_%s' % area_id)

            if not sub_data:
                # city_model_list = Area.objects.filter(parent_id=area_id)
                city_model = Area.objects.get(id=area_id)
                city_model_list = city_model.subs.all()

                # 将orm的数据对象 转换成 前端需要的json格式
                subs_list = []
                for city in city_model_list:
                    subs_list.append({'id': city.id, "name": city.name})

                sub_data = {
                    'id': city_model.id,
                    'name': city_model.name,
                    'subs': subs_list
                }

                cache.set('subs_%s' % area_id, sub_data, 3600)

            return JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'sub_data': sub_data})
