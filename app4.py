from html import escape
from webob import Response
from webob.dec import wsgify
from collections import namedtuple
import re


PATTERNS = {
    'str': '[^/].+',
    'word': '\w+',
    'any': '.+',
    'int': '[+-]?\d\+',
    'float': '[+-]?\d+\.\d+'
}


CASTS = {
    'str': str,
    'word': str,
    'any': str,
    'int': int,
    'float': float
}


Route = namedtuple('Route', ['pattern', 'methods', 'casts', 'handler'])


class Router:
    def __init__(self, prefix='', domain=None):
        self.routes = []
        self.domain = domain
        self.prefix = prefix

    def _route(self, rule, methods, handler):
        pattern, casts = self._rule_parse(rule)
        self.routes.append(Route(re.compile(pattern), methods, casts, handler))

    def _rule_parse(self, rule):
        pattern = []
        spec = []
        casts = {}
        is_spec = False
        for c in rule:
            if c == '{' and not is_spec:
                is_spec = True
            elif c == '}' and is_spec:
                is_spec = False
                name, p, c = self._spec_parse(''.join(spec))
                spec = []
                pattern.append(p)
                casts[name] = c
            elif is_spec:
                spec.append(c)
            else:
                pattern.append(c)
        return '{}$'.format(''.join(pattern)), casts

    def _spec_parse(self, src):
        tmp = src.split(':')
        if len(tmp) > 2:
            raise Exception('error pattern')
        name = tmp[0]
        type = 'str'
        if len(tmp) == 2:
            type = tmp[1]
        pattern = '(?P<{}>{})'.format(name, PATTERNS[type])
        return name, pattern, CASTS[type]

    def route(self, pattern, methods=None):
        if methods is None:
            methods = ('GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS')

        def dec(fn):
            self._route(pattern, methods, fn)
            return fn

        return dec

    def _domain_match(self, request):
        return self.domain is None or re.match(self.domain, request.host)

    def _prefix_match(self, request):
        return request.path.startswith(self.prefix)

    def match(self, request):
        if self._domain_match(request) and self._prefix_match(request):
            for route in self.routes:
                if request.method in route.methods:
                    m = route.pattern.match(request.path.replace(self.prefix, '', 1))
                    if m:
                        request.arg = {}
                        for k, v in m.groupdict().items():
                            request.args[k], = route.casts[k](v)
                        return route.handler


class Application:
    def __init__(self):
        self.routers = []

    def add_router(self, router):
        self.routers.append(router)

    @wsgify
    def __call__(self, request):
        for router in self.routers:
            handler = router.match(request)
            if handler:
                # return handler(self, request)
                return handler(request
                               )

r1 = Router() # domain='python.mageedu.com')
r2 = Router('/r2')


@r1.route(r'/$')
def main(request):
    return Response('this is main page')


@r1.route(r'/hellow$')
def hello(request):
    name = request.params.get('name', 'anon')
    body = 'hello {}'.format(escape(name))
    return Response(body)


@r2.route(r'/favicon.ico')
def favicon(requset):
    with open('./148.jpg', 'rb') as f:
        resp = Response(body=f.read(), content_type='image/x-icon')
        return resp


@r1.route(r'/148.jpg$')
def jpg(request):
    with open('./148.jpg', 'rb') as f:
        resp = Response(body=f.read(), content_type='image/jpg')
        return resp

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    app = Application()
    app.add_router(r1)
    app.add_router(r2)
    server = make_server('172.16.0.100', 8000, app)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
