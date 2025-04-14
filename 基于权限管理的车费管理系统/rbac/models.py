from django.db import models

# Create your models here.
class Role(models.Model):
    # unique=True 设置名字不能重复
    title = models.CharField(max_length=32, unique=True, verbose_name="角色名")

    # 定义角色和权限的多对多关系
    permissions = models.ManyToManyField("Permission",blank=True, verbose_name="拥有权限")

    # 定义数据模型实例对象名称
    def __str__(self):
        return self.title

    # 定义数据库表在管理后台的表名
    class Meta:
        verbose_name_plural = "角色表"

class UserInfo(models.Model):
    username = models.CharField(max_length=32)
    password = models.CharField(max_length=32)
    nickname = models.CharField(max_length=32)
    email = models.EmailField()
    roles = models.ManyToManyField("Role")
    def __str__(self):
        return self.nickname
    class Meta:
        verbose_name_plural = "用户表"

class Permission(models.Model):
    title = models.CharField(max_length=32, unique=True, verbose_name="权限名称")

    # url 字段存放URL正则表达式,用来与URL配置项对应
    url = models.CharField(max_length=128, unique=True, verbose_name="URL")

    # 权限代码字段perm_code,起到标识权限的作用,相当于权限的别名
    # 一般是list,add,del,edit
    perm_code = models.CharField(max_length=32, verbose_name="权限代码")

    """
    权限分组字段,主要作用为把一类权限分在一组中
    通过外键形式与PermGroup建立多对一的关系,一个权限组下有多个权限
    通过设置on_delete=models.CASCADE起到关联关系,外键删,记录也删
    """
    perm_group = models.ForeignKey(to='PermGroup',
                                   blank=True,
                                   on_delete=models.CASCADE,
                                   verbose_name="所属权限组")

    """
    这个外键与本表中记录进行关联,可称作内联外键
    """
    pid = models.ForeignKey(to='Permission',
                            null=True,
                            blank=True,
                            on_delete=models.CASCADE,
                            verbose_name="所属二级菜单")
    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "权限表"

class PermGroup(models.Model):
    title = models.CharField(max_length=32,verbose_name="组名称")
    menu = models.ForeignKey(to="Menu",
                             verbose_name="所属菜单",
                             blank=True,
                             on_delete=models.CASCADE)

    def __str__(self):
        return self.title
    class Meta:
        verbose_name_plural = "权限组"

class Menu(models.Model):
    title = models.CharField(max_length=32, unique=True, verbose_name="一级菜单")
    def __str__(self):
        return self.title
    class Meta:
        verbose_name_plural = "一级菜单表"


