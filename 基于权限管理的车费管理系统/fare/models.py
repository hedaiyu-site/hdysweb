from django.db import models
from rbac  import models as rbac_models
# Create your models here.

# 车辆信息数据模型
class CarInfo(models.Model):
    plate_number = models.CharField(max_length=7,verbose_name='车牌号',unique=True)
    driver = models.CharField(max_length=10,verbose_name='司机')
    # 设置每公里的单价,保留两位小数
    price = models.DecimalField(max_digits=8,decimal_places=2,verbose_name='单价')
    remarks = models.CharField(max_length=32,verbose_name='备注说明',blank=True,null=True)
    def __str__(self):
        return self.plate_number

# 人员数据模型
class LogUser(models.Model):
    # user_obj是一对一键,与RBAC模块中的数据模型UserInfo产生关联
    user_obj = models.OneToOneField(to=rbac_models.UserInfo,
                                    on_delete=models.CASCADE,
                                    null=True,
                                    blank=True)

    # 头像
    head_img = models.ImageField(upload_to='headimage',
                                 blank=True,
                                 null=True,
                                 verbose_name='头像')

    # 人员的部门
    dep = models.ForeignKey(to="Department",
                            to_field="id",
                            on_delete=models.CASCADE,
                            blank=True,
                            null=True)

    def __str__(self):
        return self.user_obj.username

# 部门数据模型
class Department(models.Model):
    # 部门名称，设置不能重复，不能为空
    dep_name = models.CharField(max_length=32,
                                verbose_name='部门名称',
                                unique=True,
                                blank=False)
    # 部门备注说明
    dep_script = models.CharField(max_length=60,verbose_name='备注',null=True)
    def __str__(self):
        return self.dep_name

# 车费信息数据模型
class Fare(models.Model):
    # 部门，Foreigonkey类型,与department形成多对一关系
    dep = models.ForeignKey(to='Department',to_field='id',on_delete=models.CASCADE)
    passenger = models.CharField(max_length=32,verbose_name='乘车人')

    # 乘坐的车辆，Foreignkey类型，与carinfo形成多对一关系
    car = models.ForeignKey(to='CarInfo',on_delete=models.CASCADE)
    driver = models.CharField(max_length=10,verbose_name='司机')
    price = models.DecimalField(max_digits=8,decimal_places=2,verbose_name='单价')
    distance = models.DecimalField(max_digits=5,decimal_places=2,verbose_name='公里数')

    # 车费,保留两位小数
    fare = models.DecimalField(max_digits=8,decimal_places=2,verbose_name='车费')

    # driver_date字段,用增加记录时的时间赋值
    drive_date = models.DateField(auto_now_add=True,verbose_name='乘车时间',blank=True,null=True)
    remark = models.CharField(max_length=100,verbose_name='乘车说明')
    oprator = models.CharField(max_length=32,verbose_name='输入人员')
    approve_date = models.DateField(verbose_name='审批时间',auto_now=True,blank=True,null=True)
    approve_status = models.CharField(max_length=1,
                                      choices=(
                                          ('0','未审批'),
                                          ('1','通过审批')
                                      ),
                                      verbose_name='审批状态',blank=True,null=True)




