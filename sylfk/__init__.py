#coding=utf-8

from werkzeug.serving import run_simple

from werkzeug.wrappers import Response

from sylfk.wsgi_adapter import wsgi_app

import sylfk.exceptions as exceptions


# 处理函数数据结构
class ExecFunc:
    def __init__(self, func, func_type, **options):
        self.func = func # 处理函数
        self.options = options # 附带参数
        self.func_type = func_type # 函数类型


class SYLFK:

    # 实例化方法
    def __init__(self, static_folder='static'):
        self.host = '127.0.0.1' # 默认主机
        self.port = 8086 # 默认端口
        self.url_map = {} # 存放 URL 与 节点（端点）的映射
        self.static_map = {} # 存放 URL 与静态资源的映射
        self.function_map = {} # 存放节点（端点）与处理请求函数的映射
        self.static_folder = static_folder # 静态资源本地存放路径，默认放在应用目录的static文件夹
    
    # 路由
    def dispatch_request(self, request):
        status = 200  # HTTP状态码定义为 200，表示请求成功

        # 定义响应报头的 Server 属性
        headers = {
        'Server': 'Simple Framework'
        }

        # 回传实现 WSGI 规范的响应体给 WSGI 模块
        return Response('<h1>Hello, Framework</h1>', content_type='text/html', headers=headers, status=status)

    # 路由添加规则
    def add_url_rule(self, url, func, func_type, endpoint=None, **options):

        # 如果节点未命名， 就使用处理函数名
        if endpoint is None:
            endpoint = func.__name__

        # 抛出 URL 已存在异常
        if url in self.url_map:
            raise exceptions.URLExistsError

        # 如果类型不是静态资源，并且节点已存在，则抛出节点已存在异常
        if endpoint in self.function_map and func_type != 'static':
            raise exceptions.EndpointExistsError

        # 添加 URL 与节点映射
        self.url_map[url] = endpoint

        # 添加节点与请求处理函数映射
        self.function_map[endpoint] = ExecFunc(func, func_type, **options)



    # 启动入口
    def run(self, host=None, port=None, **options):
        """
        初始化工作、启动服务
        """
        # 如果有参数进来且值不为空，则赋值
        for key, value in options.items():
            if value is not None:
                self.__setattr__(key, value)
        
        # 如果 host 不为 None, 替换 self.host
        if host:
            self.host = host
        
        # 如果 port 不为 None, 替换 self.port
        if port:
            self.port = port
        
        # 把框架本身也就是应用本身和其它几个配置参数传给 werkzeug 的 run_simple
        run_simple(hostname=self.host, port=self.port, application=self, **options)

    # 框架被 WSGI 调用入口的方法
    def __call__(self, environ, start_response):
        return wsgi_app(self, environ, start_response)
