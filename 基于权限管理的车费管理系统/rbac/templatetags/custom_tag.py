from django import template
from django.conf import settings
import re,os
from django.utils.safestring import mark_safe

# 生成一个模板类库
register = template.Library()
"""
处理init_permission生成的数据结构，生成系统菜单的所需的数据结构
这个函数共有3个循环
第一个循环形成二级菜单字典
第二个循环把当前二级菜单设置为'active':True
第三个循环把一级菜单，二级菜单放在一个数据结构中，并分清层次
"""
def get_structure_data(request):
    # 取出当前url
    current_url = request.path_info
    # 取出init_permission 生成的数据
    perm_menu = request.session[settings.PERMISSION_MENU_KEY]
    menu_dict = {}

    for item in perm_menu:
        if not item["pid_id"]:
            menu_dict[item["id"]]=item.copy()

    for item in perm_menu:
        regex="^{0}$".format(item['url'])
        if re.match(regex,current_url):
            if not item['pid_id']:
                menu_dict[item["id"]]["active"]=True
            else:
                menu_dict[item["pid_id"]]["active"]=True
    menu_result={}

    for item in menu_dict.values():
        active = item.get("active")
        menu_id = item.get("menu_id")
        if menu_id in menu_result:
            menu_result[menu_id]["children"].append({'title':item['title'],'url':item['url'],'active':active})
            if active:
                menu_result[menu_id]["active"]=True
        else:
            menu_result[menu_id]={
                'menu_id':menu_id,
                'menu_title':item['menu_title'],
                'active':active,
                'children':[
                    {'title':item['title'],'url':item['url'],'active':active}
                ]
            }
    return menu_result

@register.inclusion_tag("rbac_menu.html")
def rbac_menu(request):
    menu_data = get_structure_data(request)
    return {'menu_result':menu_data}
register.filter('get_structure_data',get_structure_data)