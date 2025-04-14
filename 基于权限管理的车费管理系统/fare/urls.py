from django.urls import path
from fare import views

urlpatterns = [
    # 首页
    path('index/',views.index),
    # 车辆信息查看
    path('carlist/',views.carlist),
    # 车辆信息增加
    path('caradd/',views.caradd),
    # # 车辆信息修改
    path('caredit/<int:id>/',views.caredit),
    # # 车辆信息删除
    path('cardel/<int:id>/',views.cardel),

    # 部门信息
    path('deplist/',views.deplist),
    # 部门信息增加
    path('depadd/',views.depadd),
    # 部门信息修改
    path('depedit/<int:id>/',views.depedit),
    # 部门信息删除
    path('depdel/<int:id>/',views.depdel),

    # 用户的部门管理
    path('userlist/',views.userlist),
    # 用户分配到部门
    path('useredit/<int:userid>/',views.useredit),

    # 当日车费上报
    # 本部门当日车费信息列表
    path('farelist/',views.farelist),
    # 车费信息增加
    path('fareadd/',views.fareadd),
    # # 车费信息修改
    path('fareedit/<int:fareid>/',views.fareedit),
    # # 车费信息删除
    path('faredel/<int:fareid>/',views.faredel),

    # 车费审批
    # 需要审批的记录列表
    path('farecheck/',views.farecheck),
    # 对选中的记录通过审批
    path('fareapprove/<str:ids>/',views.fareapprove),
    # 能够取消审批的记录
    path('farecheck2/',views.farecheck2),
    # 对选中的记录取消审批
    path('approvecancel/<str:ids>/',views.approve_cancel),

    # 车费统计
    path('annotate/',views.annotate_fare),
]