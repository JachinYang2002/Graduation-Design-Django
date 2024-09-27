# myapp/middleware.py
from django.http import HttpResponseForbidden

class SimpleAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # 定义白名单
        self.whitelist = [
            '^/api/user/login/',  # 登录页面
            '^/api/user/register/',  # 注册页面
            # 其他白名单路径
        ]

    def __call__(self, request):
        # 检查白名单
        path = request.path_info
        if any(path.startswith(whitelist) for whitelist in self.whitelist):
            response = self.get_response(request)
            return response

        # 检查用户是否登录以及是否具有权限
        if not request.user.is_authenticated:
            return HttpResponseForbidden("请先登录")

        # 这里可以添加更多的权限检查逻辑

        response = self.get_response(request)
        return response