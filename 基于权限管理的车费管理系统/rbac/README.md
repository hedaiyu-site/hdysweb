# RBAC (基于角色的访问控制) 模块文档

## 概述
本RBAC模块实现了基于角色的权限管理系统，包含以下核心功能：
- 角色管理
- 用户管理
- 权限管理
- 权限组管理
- 菜单管理
- 权限验证中间件
- 权限初始化服务
- 前端菜单标签

## 模型说明

### 1. 角色模型 (Role)
- `title`: 角色名称(唯一)
- `permissions`: 与权限的多对多关系
- 元数据: 表名为"角色表"

### 2. 用户模型 (UserInfo)
- `username`: 用户名
- `password`: 密码
- `nickname`: 昵称
- `email`: 邮箱
- `roles`: 与角色的多对多关系
- 元数据: 表名为"用户表"

### 3. 权限模型 (Permission)
- `title`: 权限名称(唯一)
- `url`: URL正则表达式(唯一)
- `perm_code`: 权限代码(如list,add,del,edit)
- `perm_group`: 所属权限组(外键)
- `pid`: 所属二级菜单(自关联外键)
- 元数据: 表名为"权限表"

### 4. 权限组模型 (PermGroup)
- `title`: 组名称
- `menu`: 所属菜单(外键)
- 元数据: 表名为"权限组"

### 5. 菜单模型 (Menu)
- `title`: 一级菜单名称(唯一)
- 元数据: 表名为"一级菜单表"

## 核心组件

### 1. 权限中间件 (RbacMiddleware)
位置: `rbac/middleware/rbac.py`
功能:
- 处理每个请求的权限验证
- 检查URL是否在白名单(SAFE_URL)
- 超级用户跳过权限检查
- 未登录用户重定向到登录页
- 验证用户权限并设置session中的权限代码

### 2. 权限初始化服务 (init_permission.py)
位置: `rbac/service/init_permission.py`
功能:
- 用户登录后初始化权限
- 从数据库获取用户的所有权限
- 将权限URL转换为正则表达式
- 按权限组整理权限数据
- 将权限URL列表和菜单数据存入session

### 3. 菜单标签 (custom_tag.py)
位置: `rbac/templatetags/custom_tag.py`
功能:
- 生成菜单数据结构
- 根据当前URL标记活动菜单
- 提供`rbac_menu`模板标签
- 支持在模板中使用`{% rbac_menu request %}`渲染菜单

## 使用流程

1. **用户登录**
   - 调用`init_permission(request, user_obj)`初始化权限

2. **权限验证**
   - 中间件自动验证每个请求的权限
   - 白名单URL直接放行
   - 未授权用户返回提示信息

3. **菜单生成**
   - 在模板中使用`{% load custom_tag %}`
   - 使用`{% rbac_menu request %}`渲染菜单

4. **权限检查**
   - 通过`request.session['permission_codes']`获取权限代码
   - 在视图或模板中检查具体权限

## 配置说明
在Django settings.py中添加以下配置: