"""
该文件主要为两个功能,
一是根据用户所属角色从数据库中获取此用户的权限,然后按一定的数据格式
存放在request.session中;

二是把该用户涉及的菜单,权限组,权限等信息按数据表关联关系取出,按一定的数据格式也存放在
request.session中
"""
import re

from django.conf import settings

"""
这个函数一般是在用户登录后接着调用,根据用户权限进行数据初始化
初始化用户权限,写入session中
参数request是Request请求对象
参数user_obj是登录用户对象,取自UserInfo表
"""
def init_permission(request, user_obj):
    """
    按照ORM查询语句取值
    """
    permission_item_list = user_obj.roles.values('permissions__id',
                                                 'permissions__title',
                                                 'permissions__url',
                                                 'permissions__perm_code',
                                                 'permissions__pid_id',
                                                 'permissions__perm_group_id',
                                                 'permissions__perm_group__menu_id',
                                                 'permissions__perm_group__menu__title').distinct()
    permission_url_list = {}
    permission_menu_list = []

    for item in permission_item_list:
        perm_group_id = item['permissions__perm_group_id']
        url = item['permissions__url']
        url = re.sub('<int:\\w+>','[0-9]+',url)
        url = re.sub('<str:\\w+>','[^/]+',url)
        url = re.sub('<slug:\\w+>','[-a-zA-Z0-9]+',url)
        url = re.sub('<uuid:\\w+>','[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}+',url)
        url = re.sub('<path:\\w+>','.+',url)
        perm_code = item['permissions__perm_code']
        if perm_group_id in permission_url_list:
            permission_url_list[perm_group_id]['codes'].append(perm_code)
            permission_url_list[perm_group_id]['urls'].append(url)
        else:
            permission_url_list[perm_group_id] = {'codes':[perm_code,],
                                                  'urls':[url,]}

    # 把permission_url_list存放在session中
    # session中的键名用的是setting.py文件中PERMISSION_URL_KEY变量的值
    # 前提是setting.py文件设有这个变量
    request.session[settings.PERMISSION_URL_KEY]=permission_url_list

    for item in permission_item_list:
        tpl = {
            'id':item['permissions__id'],
            'title':item['permissions__title'],
            'url':item['permissions__url'],
            'pid_id':item['permissions__pid_id'],
            'menu_id':item['permissions__perm_group__menu_id'],
            'menu_title':item['permissions__perm_group__menu__title']
        }
        permission_menu_list.append(tpl)
    request.session[settings.PERMISSION_MENU_KEY]=permission_menu_list

