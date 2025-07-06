import datetime

from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import render, redirect,HttpResponse
from django.conf import settings

from rbac import models as rbac_models
from rbac.service.init_permission import init_permission
from utils.paginater import Paginater
from . import models


# Create your views here.
class BasePermPage(object):
    # 类的初始化函数,code_list参数是接收request.session['permission_codes']的值
    # request.session['permission_codes']的值在rbac模块的中间件RbacMiddleware中赋予
    def __init__(self,code_list):
        self.code_list = code_list

    def has_add(self):
        if "add" in self.code_list:
            return 1

    def has_del(self):
        if "del" in self.code_list:
            return True

    def has_edit(self):
        if "edit" in self.code_list:
            return True

# def index_1(request):
#     return HttpResponse("测试")

def index(request):
    #messages.success(request,'登录成功')
    return render(request, 'index.html')


def login(request):
    if request.method == 'GET':
        return render(request, "fare/login.html")

    else:
        username = request.POST.get('username')
        password = request.POST.get('password')
        # 利用rbac模块中UserInfo的数据记录判断用户名和密码是否正确
        user = rbac_models.UserInfo.objects.filter(username=username,
                                                   password=password).first()
        if user:
            # 对用户权限初始化
            init_permission(request,user)
            # 用session保存用户名称与部门代码，供其他视图函数使用
            request.session['user_nickname'] = user.nickname
            request.session['user_dep'] = user.loguser.dep_id
            messages.success(request, '登录成功'),
            return redirect("/fare/index/")

        else:
            messages.success(request, '登录失败，请检查账号或密码'),
            return render(request, "fare/login.html")


def logout(request):
    # 清除session中的值
    request.session.clear()
    rep = redirect('login')
    # 清除cookie中的值
    rep.cookies.clear()
    return rep


# 车辆信息相关
def carlist(request):
    pagpermission=BasePermPage(request.session.get('permission_codes'))
    carlist = models.CarInfo.objects.all()
    # 向模板文件传递变量，并把保存BasePermPage实例化对象的变量传递过去
    return render(request, 'fare/carinfo_list.html', {'carlist': carlist,'pagpermission':pagpermission})


def caradd(request):
    if request.method == "POST":
        # 依次取出前端页面表单中提交到后端的数据
        plate_number = request.POST.get('plate_number')
        driver = request.POST.get('driver')
        price = request.POST.get('price')
        remarks = request.POST.get('remarks')

        if plate_number and driver and price:
            models.CarInfo.objects.create(plate_number=plate_number,
                                          driver=driver,
                                          price=price,
                                          remarks=remarks)
            return redirect('/fare/carlist/', )
    return render(request, 'fare/carinfo_add.html')


def caredit(request, id):
    if request.method == 'POST':
        # 取出前端提交的id值
        obj_id = request.POST.get("id")
        # 根据id值从数据库表中取出记录
        car_obj = models.CarInfo.objects.get(id=obj_id)
        # 依次从前端表中取出数据
        plate_number = request.POST.get('plate_number')
        driver = request.POST.get('driver')
        price = request.POST.get('price')
        remarks = request.POST.get('remarks')
        # 依次给字段赋值
        car_obj.plate_number = plate_number
        car_obj.driver = driver
        car_obj.price = price
        car_obj.remarks = remarks
        # 保存到数据库中
        car_obj.save()
        # 返回信息页
        return redirect('/fare/carlist/')
    # 如果不是POST，从数据库表中取出记录
    car_obj = models.CarInfo.objects.get(id=id)
    # 把修改记录传给页面
    return render(request, 'fare/carinfo_edit.html', {'obj': car_obj})


def cardel(request, id):
    car_obj = models.CarInfo.objects.get(id=id)
    car_obj.delete()
    return redirect('/fare/carlist/')


# 部门相关
def deplist(request):
    pagpermission = BasePermPage(request.session.get('permission_codes'))
    dep_list = models.Department.objects.all()
    return render(request, 'fare/dep_list.html', {'deplist': dep_list,'pagpermission':pagpermission})


def depadd(request):
    if request.method == 'POST':
        dep_name = request.POST.get('dep_name')
        dep_script = request.POST.get('dep_script')
        if dep_name and dep_script:
            models.Department.objects.create(dep_name=dep_name,
                                             dep_script=dep_script)
            return redirect('/fare/deplist')
    return render(request, 'fare/dep_add.html')


def depedit(request, id):
    if request.method == 'POST':
        # 取出前端提交的id值
        obj_id = request.POST.get("id")
        # 根据id值从数据库表中取出记录
        dep_obj = models.Department.objects.get(id=obj_id)
        # 依次从前端表中取出数据
        dep_name = request.POST.get('dep_name')
        dep_script = request.POST.get('dep_script')
        # 依次给字段赋值
        dep_obj.dep_name = dep_name
        dep_obj.dep_script = dep_script
        # 保存到数据库中
        dep_obj.save()
        # 返回信息页
        return redirect('/fare/deplist/')
    # 如果不是POST，从数据库表中取出记录
    dep_obj = models.Department.objects.get(id=id)
    # 把修改记录传给页面
    return render(request, 'fare/dep_edit.html', {'obj': dep_obj})


def depdel(request, id):
    dep_obj = models.Department.objects.get(id=id)
    dep_obj.delete()
    return redirect('/fare/deplist/')


# 用户列表
def userlist(request):
    user_list = rbac_models.UserInfo.objects.all()
    return render(request, 'fare/userinfo_list.html', {"user_list": user_list})


# 用户分配到部门
def useredit(request, userid):
    if request.method == 'POST':
        # 从UserInfo中取出记录
        id = request.POST.get('id')
        user_obj = rbac_models.UserInfo.objects.get(id=id)
        dep_id = request.POST.get('dep_id')
        try:
            loguser_id = user_obj.loguser.id
            # 如果记录不存在,也就是filter()查询为空,update()会报错
            models.LogUser.objects.filter(id=loguser_id).update(dep_id=dep_id)
        except ObjectDoesNotExist:
            # 当loguser没有记录时,新建一条记录
            models.LogUser.objects.create(dep_id=dep_id,
                                          user_obj_id=id)
        return redirect('/fare/userlist')
    user_obj = rbac_models.UserInfo.objects.get(id=userid)
    dep_list = models.Department.objects.all()
    return render(request, 'fare/userinfo_edit.html', {'obj': user_obj, 'deplist': dep_list})


# 车费信息相关
def farelist(request):
    pagpermission = BasePermPage(request.session.get('permission_codes'))
    # 取得系统当前日期
    tday = datetime.datetime.now().date()
    # 从session中取出登录用户的部门，用户部门的值是在login()视图函数中存的
    cur_dep = request.session.get('user_dep')
    # 取出当天，本部门，未审批的记录(approve_status='0)
    fare_list = models.Fare.objects.all().filter(drive_date=tday,
                                                 dep_id=cur_dep,
                                                 approve_status='0')
    return render(request, 'fare/fare_list.html', {'fare_list': fare_list,'pagpermission':pagpermission})


def faredel(request, fareid):
    try:
        # 执行删除操作
        models.Fare.objects.get(id=fareid).delete()
        messages.success(request, '删除成功')
        return JsonResponse({"status": True})
    except Exception as e:
        messages.success(request, '删除失败')
        return JsonResponse({"status": False}, status=400)


def fareadd(request):
    tday = datetime.datetime.now().strftime('%Y-%m-%d')
    cur_dep = request.session.get('user_dep')
    dep_obj = models.Department.objects.get(id=cur_dep)
    # 取出车辆信息记录
    car_list = models.CarInfo.objects.all()
    user_nickname = request.session.get('user_nickname')
    if request.method == 'POST':
        passenger = request.POST.get('passenger')
        carid = request.POST.get('car_id')
        driver = request.POST.get('driver')
        price = request.POST.get('price')
        distance = request.POST.get('distance')
        fare = request.POST.get('fare')
        remark = request.POST.get('remark')
        # 赋值日期
        drive_date = datetime.datetime.now().date()
        # 插入数据库
        models.Fare.objects.create(dep_id=cur_dep,
                                   passenger=passenger,
                                   car_id=carid,
                                   driver=driver,
                                   price=price,
                                   distance=distance,
                                   fare=fare,
                                   drive_date=drive_date,
                                   remark=remark,
                                   oprator=user_nickname,
                                   approve_status='0')
        return redirect('/fare/farelist')
    return render(request, 'fare/fare_add.html', locals())


def fareedit(request, fareid):
    # 按照一定格式取出当前日期
    tday = datetime.datetime.now().strftime('%Y-%m-%d')
    # 从session中取出登录用户的部门
    cur_dep = request.session.get('user_dep')
    # 取出部门对象和车辆
    dep_obj = models.Department.objects.get(id=cur_dep)
    car_list = models.CarInfo.objects.all()
    user_nickname = request.session.get('user_nickname')
    if request.method == 'POST':
        fareid = request.POST.get('id')
        cur_dep = request.POST.get('dep_id')
        passenger = request.POST.get('passenger')
        carid = request.POST.get('car_id')
        driver = request.POST.get('driver')
        price = request.POST.get('price')
        distance = request.POST.get('distance')
        fare = request.POST.get('fare')
        remark = request.POST.get('remark')
        drive_date = request.POST.get('drive_date')
        # 修改记录
        models.Fare.objects.filter(id=fareid).update(dep_id=cur_dep,
                                                     passenger=passenger,
                                                     car_id=carid,
                                                     driver=driver,
                                                     price=price,
                                                     distance=distance,
                                                     fare=fare,
                                                     drive_date=drive_date,
                                                     remark=remark,
                                                     oprator=user_nickname
                                                     )
        return redirect('/fare/farelist')
    fare_obj = models.Fare.objects.get(id=fareid)
    car_list = models.CarInfo.objects.all()
    return render(request, 'fare/fare_edit.html', {'obj': fare_obj, 'carlist': car_list})


# 车费审批相关
def farecheck(request):
    # 取出部门记录
    dep_list = models.Department.objects.all()
    if request.method == 'POST':
        # 取出查询值，部门，乘车时间
        dep_id = request.POST.get('department', None)
        drive_date1 = request.POST.get('drive_date1', None)
        drive_date2 = request.POST.get('drive_date2', None)
        # 初始化一个空字典，用来放置查询条件
        condition_dic = {}
        # 需要审批的记录应该是上报后未审批的记录，因此第一个条件是approve_status=0
        condition_dic['approve_status'] = '0'
        # 如果部门值不为空，设置为查询条件
        if dep_id:
            condition_dic['dep_id'] = int(dep_id)
        # 设置乘车时间范围
        if drive_date1:
            # 设置字典键名为drive_date__gte
            condition_dic['drive_date__gte'] = drive_date1
        if drive_date2:
            condition_dic['drive_date__lte'] = drive_date2
        # 如果字典项不为0，则生成过滤条件进行查询，字典项为空时，查询全部记录
        if len(condition_dic) > 0:
            # 取得总记录数
            total_count = models.Fare.objects.filter(**condition_dic).count()
        else:
            total_count = models.Fare.objects.all().count()
        cur_page_num = request.GET.get("page")
        if not cur_page_num:
            cur_page_num = "1"

        # 设置每一页显示多少条记录
        one_page_lines = 10
        # 页面上总共展示多少页码标签
        page_maxtag = 7

        # 生成一个分页对象
        page_obj = Paginater(url_address='/fare/farecheck/',
                             cur_page_num=cur_page_num,
                             total_rows=total_count,
                             one_page_lines=one_page_lines,
                             page_maxtag=page_maxtag)

        if len(condition_dic) > 0:
            # 对记录进行切片,取出属于当前页的记录
            fare_list = models.Fare.objects.filter(**condition_dic).order_by('drive_date')[
                        page_obj.data_start:page_obj.data_end]
        else:
            # 当查询条件为空时，取出属于当前页的记录
            fare_list = models.Fare.objects.all().order_by('drive_date')[page_obj.data_start:page_obj.data_end]
        return render(request, 'fare/farelist_check.html', {'fare_list': fare_list,
                                                            'page_nav': page_obj.html_page(),
                                                            'dep_list': dep_list,
                                                            'conditions': condition_dic})
    # 当提交方式不是post，说明是初次打开页面
    cur_page_num = request.GET.get('page')
    if not cur_page_num:
        cur_page_num = "1"

    total_count = models.Fare.objects.filter(approve_status='0').count()
    one_page_lines = 10
    page_maxtag = 7
    page_obj = Paginater(url_address='/fare/farecheck/',
                         cur_page_num=cur_page_num,
                         total_rows=total_count,
                         one_page_lines=one_page_lines,
                         page_maxtag=page_maxtag)

    fare_list = models.Fare.objects.filter(approve_status='0').order_by('drive_date')[
                page_obj.data_start:page_obj.data_end]
    return render(request, 'fare/farelist_check.html', {'fare_list': fare_list,
                                                        'page_nav': page_obj.html_page(),
                                                        'dep_list': dep_list,
                                                        })


def fareapprove(request, ids):
    vids = ids.split(',')
    int_ids = []
    for i in vids:
        ii = int(i)
        int_ids.append(ii)
    # ret = {'status':False}
    try:
        models.Fare.objects.filter(id__in=vids).update(approve_status='1')
        # ret['status']=True
        return JsonResponse({'status': True})
    except Exception as e:
        # ret['status']=False
        return JsonResponse({'status': False, 'error': str(e)})


# 取消审批
def farecheck2(request):
    # 取出部门记录
    dep_list = models.Department.objects.all()
    if request.method == 'POST':
        # 取出查询值，部门，乘车时间
        dep_id = request.POST.get('department', None)
        drive_date1 = request.POST.get('drive_date1', None)
        drive_date2 = request.POST.get('drive_date2', None)
        # 初始化一个空字典，用来放置查询条件
        condition_dic = {}
        # 需要审批的记录应该是上报后未审批的记录，因此第一个条件是approve_status=0
        condition_dic['approve_status'] = '1'
        # 如果部门值不为空，设置为查询条件
        if dep_id:
            condition_dic['dep_id'] = int(dep_id)
        # 设置乘车时间范围
        if drive_date1:
            # 设置字典键名为drive_date__gte
            condition_dic['drive_date__gte'] = drive_date1
        if drive_date2:
            condition_dic['drive_date__lte'] = drive_date2
        # 如果字典项不为0，则生成过滤条件进行查询，字典项为空时，查询全部记录
        if len(condition_dic) > 0:
            # 取得总记录数
            total_count = models.Fare.objects.filter(**condition_dic).count()
        else:
            total_count = models.Fare.objects.all().count()
        cur_page_num = request.GET.get("page")
        if not cur_page_num:
            cur_page_num = "1"

        # 设置每一页显示多少条记录
        one_page_lines = 10
        # 页面上总共展示多少页码标签
        page_maxtag = 7

        # 生成一个分页对象
        page_obj = Paginater(url_address='/fare/farecheck2/',
                             cur_page_num=cur_page_num,
                             total_rows=total_count,
                             one_page_lines=one_page_lines,
                             page_maxtag=page_maxtag)

        if len(condition_dic) > 0:
            # 对记录进行切片,取出属于当前页的记录
            fare_list = models.Fare.objects.filter(**condition_dic).order_by('drive_date')[
                        page_obj.data_start:page_obj.data_end]
        else:
            # 当查询条件为空时，取出属于当前页的记录
            fare_list = models.Fare.objects.all().order_by('drive_date')[page_obj.data_start:page_obj.data_end]
        return render(request, 'fare/farelist_check2.html', {'fare_list': fare_list,
                                                             'page_nav': page_obj.html_page(),
                                                             'dep_list': dep_list,
                                                             'conditions': condition_dic,
                                                             })
    # 当提交方式不是post，说明是初次打开页面
    cur_page_num = request.GET.get('page')
    if not cur_page_num:
        cur_page_num = "1"

    total_count = models.Fare.objects.filter(approve_status='0').count()
    one_page_lines = 10
    page_maxtag = 7
    page_obj = Paginater(url_address='/fare/farecheck2/',
                         cur_page_num=cur_page_num,
                         total_rows=total_count,
                         one_page_lines=one_page_lines,
                         page_maxtag=page_maxtag)

    fare_list = models.Fare.objects.filter(approve_status='1').order_by('drive_date')[
                page_obj.data_start:page_obj.data_end]
    return render(request, 'fare/farelist_check2.html', {'fare_list': fare_list,
                                                         'page_nav': page_obj.html_page(),
                                                         'dep_list': dep_list,
                                                         })


# 取消审批
def approve_cancel(request, ids):
    vids = ids.split(',')
    int_ids = []
    for i in vids:
        ii = int(i)
        int_ids.append(ii)
    # ret = {'status':False}
    try:
        models.Fare.objects.filter(id__in=vids).update(approve_status='0')
        # ret['status']=True
        return JsonResponse({'status': True})
    except Exception as e:
        # ret['status']=False
        return JsonResponse({'status': False, 'error': str(e)})


def annotate_fare(request):
    # 通过annotate()进行分组和聚合，这个查询语句的第一个values()中的字段是分组函数
    # 第二个value()中的字段是要显示值的字段
    # 注意字段可以通过__进行联表查询
    farelist = models.Fare.objects.values("dep__dep_name",
                                          "drive_date__year",
                                          "drive_date__month",
                                          "approve_status").annotate(sum_distance=Sum("distance"),
                                                                     sum_fare=Sum("fare")).values("dep__dep_name",
                                                                                                  "drive_date__year",
                                                                                                  "drive_date__month",
                                                                                                  "approve_status",
                                                                                                  "sum_distance",
                                                                                                  "sum_fare")
    # 初始换字典，保存后台数据
    faredic = {}
    # 设置一个标志字段，表明是否循坏刚开始的第一条记录
    begin = True
    # 初始化一个字段用来保存部门名称
    depname = ''
    # 保存未经审批的行车里程小计
    distance0_xj = 0
    # 保存未经审批的费用小计
    fare0_xj=0
    # 保存经过审批的行车里程小计
    distance1_xj = 0
    # 保存经过审批的费用小计
    fare1_xj = 0
    # 行车总里程小计
    distance_xj = 0
    # 行车费用小计
    fare_xj = 0
    # 未经审批的行车里程合计
    distance0_hj = 0
    # 未经审批的行车费用合计
    fare0_hj = 0
    # 经过审批的行车里程合计
    distance1_hj = 0
    # 经过审批的行车费用合计
    fare1_hj = 0
    # 行车里程合计
    distance_hj = 0
    # 车费合计
    fare_hj = 0
    # 通过for取得分组记录
    for fare in farelist:
        # 如果是第一条记录,把部门名称赋给depname
        if begin:
            begin = False
            depname = fare["dep__dep_name"]

        # 在部门发生变化前，插入一条小计记录
        if depname!=fare["dep__dep_name"]:
            onefare = {'dep__dep_name':'小计',
                       'sum_distance0':distance0_xj,
                       'sum_fare0':fare0_xj,
                       'sum_distance1':distance1_xj,
                       'sum_fare1':fare1_xj,
                       'sum_distance':distance_xj,
                       'sum_fare':fare_xj}
            faredic[depname+'xj'] = onefare
            # 把各个小计设为0
            distance0_xj = 0
            fare0_xj = 0
            distance1_xj = 0
            fare1_xj = 0
            distance_xj = 0
            fare_xj = 0
            # 把新的部门名称赋给depname
            depname = fare["dep__dep_name"]

        # 把每条记录对应的字段值加到对应的小计值中
        distance_xj += fare["sum_distance"]
        fare_xj += fare["sum_fare"]
        distance_hj += fare["sum_distance"]
        fare_hj += fare["sum_fare"]

        # 根据审批状态，把每条记录的字段值加到对应的小计，合计中
        if fare["approve_status"] == '0':
            distance0_xj += fare["sum_distance"]
            fare0_xj += fare["sum_fare"]
            distance0_hj += fare["sum_distance"]
            fare0_hj += fare["sum_fare"]

        if fare["approve_status"] == '1':
            distance1_xj += fare["sum_distance"]
            fare1_xj += fare["sum_fare"]
            distance1_hj += fare["sum_distance"]
            fare1_hj += fare["sum_fare"]
        # 生成一个唯一标识，用这个标识标志一条记录
        # 这里用部门名称，乘车日期的年，月组合成这个标识vid
        vid = fare["dep__dep_name"] + str(fare["drive_date__year"]) + str(fare["drive_date__month"])

        # 判断字典是否有键名等于vid值的键
        if vid in faredic:
            """
            循环每一条记录
            根据记录的approve_status的值，生成faredic[vid]中不同的值
            也就是说下面两个if生成faredic[vid]中不同的值
            也就是二级字典键值对
            """
            if fare["approve_status"] == '0':
                # 在faredic[vid]的值中，增加一个项目是字典类型，相当于一个二级字典
                faredic[vid]["sum_distance0"] = fare["sum_distance"]
                faredic[vid]["sum_fare0"] = fare["sum_fare"]

            if fare["approve_status"] == '1':
                faredic[vid]["sum_distance1"] = fare["sum_distance"]
                faredic[vid]["sum_fare1"] = fare["sum_fare"]

            # 当sum_distance0为键名的项在faredic[vid]中
            # 说明当前记录是未经审批的记录，把行车里程和车费都取出放进变量
            if "sum_distance0" in faredic[vid]:
                distance0 = faredic[vid]["sum_distance0"]
                fare0 = faredic[vid]["sum_fare0"]
            else:
                distance0 = 0
                fare0 = 0

            # 当sum_distance1为键名
            # 说明是审批了的记录
            if "sum_distance1" in faredic[vid]:
                distance1 = faredic[vid]["sum_distance1"]
                fare1 = faredic[vid]["sum_fare1"]
            else:
                distance1 = 0
                fare1 = 0
            # 在faredic[vid]的项中增加两个键值对
            # sum_distance为未经审批的行车里程与经过审批的行车里程的和
            # sum_fare为未经过与经过审批的车费和
            faredic[vid]["sum_distance"] = distance0 + distance1
            faredic[vid]["sum_fare"] = fare0 + fare1

        else:
            # 如果字典中不存在vid键,新增
            onefare = {'dep__dep_name':fare["dep__dep_name"],
                       'drive_date__year':fare["drive_date__year"],
                       'drive_date__month':fare["drive_date__month"],}

            if fare["approve_status"] == '0':
                onefare["sum_distance0"] = fare["sum_distance"]
                onefare["sum_fare0"] = fare["sum_fare"]

            if fare["approve_status"] == '1':
                onefare["sum_distance1"] = fare["sum_distance"]
                onefare["sum_fare1"] = fare["sum_fare"]

            # 在faredic中加入一个键值对，键名等于vid变量的值值未onefare
            faredic[vid] = onefare
            # 当sum_distance0为键名的项在faredic[vid]中
            # 说明当前记录是未审批状态
            if "sum_distance0" in onefare:
                distance0 = onefare["sum_distance0"]
                fare0 = onefare["sum_fare0"]
            else:
                distance0 = 0
                fare0 = 0

            # 当sum_distance1为键名的项在faredic[vid]中
            # 说明当前记录是审批状态
            if "sum_distance1" in onefare:
                distance1 = onefare["sum_distance1"]
                fare1 = onefare["sum_fare1"]
            else:
                distance1 = 0
                fare1 = 0

            # # 在faredic[vid]的项中增加两个键值对
            # # sum_distance为未经审批的行车里程与经过审批的行车里程的和
            # # sum_fare为未经过与经过审批的车费和
            onefare["sum_distance"] = distance0 + distance1
            onefare["sum_fare"] = fare0 + fare1
            faredic[vid] = onefare

    # 在循环外，在字典中加入最后一个部门的小计
    onefare = {"dep__dep_name":"小计",
               "sum_distance0":distance0_xj,
               "sum_fare0":fare0_xj,
               "sum_distance1":distance1_xj,
               "sum_fare1":fare1_xj,
               "sum_distance":distance_xj,
               "sum_fare":fare_xj}
    faredic[depname + 'xj'] = onefare
    # 在循环外,在字典中加合计项
    onefare = {"dep__dep_name": "合计",
               "sum_distance0": distance0_hj,
               "sum_fare0": fare0_hj,
               "sum_distance1": distance1_hj,
               "sum_fare1": fare1_hj,
               "sum_distance": distance_hj,
               "sum_fare": fare_hj}
    faredic[depname + 'hj'] = onefare
    return render(request,'fare/fare_addup.html',{'faredic':faredic,})


