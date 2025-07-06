from django.conf import settings
from django.shortcuts import HttpResponse,redirect
from django.utils.deprecation import MiddlewareMixin
import re

class RbacMiddleware(MiddlewareMixin):
    """
    process_request()方法，是中间件原有的方法
    这个方法在客户端发出request请求后，执行视图函数前调用
    任何request请求都会先调用process_request()方法
    该方法五返回，返回None或HttpResponse对象时，程序继续执行其他中间件
    直到执行相应的视图
    如果它返回一个HttpResponse对象，程序中断执行，向客户端返回HttpResponse
    我们重写这个方法，主要判断登录用户对当前要访问的URL是否有权限
    如果有权限则返回None，程序继续往下执行，无权则返回HttpResponse对象中止程序向下运行
    """
    def process_request(self, request):
        # 请求中取得URL，这个地址是用户请求地址
        # request.path_info得到请求路径
        # 如http://127.0.0.1:8000/index/的path_info是/index/
        request_url = request.path_info

        # 从session中取出init_permission中生成的字典，这个字典包含用户可以访问的URL
        permission_url = request.session.get(settings.PERMISSION_URL_KEY)

        # 在setting.py文件中，SAFE_URL保存无需权限，直接访问的URL
        # 称为URL白名单
        # 如果请求URL在白名单，直接return None放行
        for url in settings.SAFE_URL:
            if re.match(url, request_url):
                return None
        # 如果是超级用户，不进行权限筛查
        if request.user.is_superuser:
            return None
        # 如果未取得permission_url，说明用户没登录，重定向到登录页面
        if not permission_url:
            return redirect(settings.LOGIN_URL)
        flag = False

        """
        通过for perm_group_id,code_url in permission_url.items()循环
        取出一级字典的键与值
        通过 for url in code_url['urls']循环取URL
        用这个URL生成正则表达式(url_pattern = "^{0}$".format(url)
        如果用户请求访问的地址与这个表达式匹配，说明用户有权限
        """
        for perm_group_id,code_url in permission_url.items():
            for url in code_url['urls']:
                url_pattern = "^{0}$".format(url)

                if re.match(url_pattern, request_url):
                    # 把权限代码放在session中
                    request.session['permission_codes'] = code_url["codes"]
                    flag = True
                    break
            if flag:
                return None

        if not flag:
            if settings.DEBUG:
                info = '<br/>' + ('<br/>'.join(code_url['urls']))
                return HttpResponse('无权限，请尝试访问以下地址: %s' % info)
            else:
                return HttpResponse('无权限访问')
