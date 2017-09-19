from html import escape
from webob import Request, Response
from webob.dec import wsgify
from collections import namedtuple
import re

Router = namedtuple('Router', ['pattern', 'method', 'handler'])


class Application
    def __init__(self):
        self.routes = []

    def _router(self, pattern, method, handler):
        self.routes.append(Router(pattern, method, handler))

    def route(self, pattern, methods=None):
        if methods is None:
            methods = ('GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS')

        def dec(fn):
            self._router(pattern, methods, fn)
            return fn
        return dec

    @wsgify
    def __call__(self, request):
        for route in self.routes:
            if request.method in route.methods:
                if re.match(route.pattern, request.path):
                    return route.handler(request)



app = Application()


@app.route(r'/$')
def main(request):
    return Response('this is main page')


@app.route(r'/hellow$')
def hello(request):
    name = request.params.get('name', 'anon')
    body = 'hello {}'.format(escape(name))
    return Response(body)


@app.route(r'/favicon.ico')
def favicon(requset):
    with open('./favicon.ico', 'rb') as f:
        resp = Response(body=f.read(), content_type= 'image/x-icon')
        return resp


if __name__ == '__main__':
    from wsgiref.simple_server import make_server

    server = make_server('172.16.0.100', 8000, app)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
