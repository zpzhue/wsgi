from html import escape
from webob import Request, Response
from webob.dec import wsgify


@wsgify
def applcation(request):
    name = request.params.get('name', 'anon')
    body = 'hello {}'.format(escape(name))
    return  Response(body)

# def applcation(environ, start_response):
#     request = Request(environ)
#     name = request.params.get('name', 'anon')
#     body = 'hello {}'.format(escape(name))
#     resp = Response(body)
#     return resp(environ, start_response)

if __name__ == '__main__':
    from wsgiref.simple_server import make_server

    server = make_server('172.16.0.100', 8000, applcation)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
