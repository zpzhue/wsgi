from urllib.parse import parse_qs
from html import  escape
import os


class Request:
    def __init__(self, environ):
        self.params = parse_qs(environ.get('QUERY_STRING'))
        self.path = environ.get('PATH_INFO')
        self.method = environ.get('wsgi.input')
        self.hearders = {}
        server_env = os.environ
        for k, v in environ.items():
            if k not in server_env.keys():
                self.hearders[k.lower()] = v


class Respones:
    STATUS = {
        200: 'OK',
        404: 'NOT Found'
    }

    def __init__(self, body=None):
        if body is None:
            body = ''
        self.body = body
        self.status = '200 OK'
        self.headers = {
            'content-type': 'text/plain',
            'content-length': str(len(self.body))
        }

    def set_body(self, body):
        self.body = body
        self.headers['content-length'] = str(len(self.body))

    def set_status(self, status_code, status_text=''):
        self.status = '{} {}'.format(status_code, self.STATUS.get(status_code, ''))

    def set_header(self, name, value):
        self.headers[name] = value

    def __call__(self, start_response):
        start_response(self.status, [(k, v) for k, v in self.headers.items()])
        return [self.body.encode()]


def applcation(environ, start_response):
    # body = 'Hello Word!'
    # status = '200 OK'
    # hearders = [
    #     ('content-type', 'text/plain'),
    #     ('content-length', str(len(body)))
    # ]
    # start_response(status, hearders)
    # return [body.encode()]

    request = Request(environ)
    name = request.params.get('name', ['anon'])[0]
    body = 'hello {}'.format(escape(name))
    return Respones(body)(start_response)

if __name__ == '__main__':
    from wsgiref.simple_server import make_server

    server = make_server('172.16.0.100', 8000, applcation)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
