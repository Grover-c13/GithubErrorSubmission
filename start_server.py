from wsgiref import simple_server

import falcon

import log_resource

app = falcon.API(media_type='application/json;  charset=UTF-8')
app.add_route('/exception', log_resource.LogResource())

if __name__ == '__main__':
    httpd = simple_server.make_server('', 8000, app)
    httpd.serve_forever()
