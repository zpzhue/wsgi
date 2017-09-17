def Applcation(environ, start_respones):
    body = 'Hello Word!'
    status = '200 OK'
    hearders = [
        ('content-type', 'text/plain'),
        ('content-length', str(len(body)))
    ]
    start_respones(status, hearders)
    return [body.encode()]


if __name__ == '__main__':
    from wsgiref.simple_server import make_server

    server = make_server('172.16.0.100', 8000, Applcation)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()