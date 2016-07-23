import httplib
from conf import __conf__
import gzip
import StringIO
import base64


class LoginFailedException(Exception):
    pass


class Response():
    '''Minix Response Class
        @Attribute headers
        @Attribute body
        @Attribute status
    '''

    def __init__(self, headers, body, status):
        self.headers = headers
        self.body = body
        self.status = status


class Request():
    '''simplify network interface, using httplib
        host, port and protocol (http or https) is loaded from configuration object
        provide compress feature (gzip), default value is True
    '''

    def __init__(self, method, url, body=None, headers=None, compress=True, server='scheduler'):
        if server == 'scheduler':
            if __conf__['webSetting'].get('https'):
                conn = httplib.HTTPSConnection(__conf__['webSetting']['host'],
                                               __conf__['webSetting']['port'],
                                               key_file=__conf__['webSetting']['keyfile'],
                                               cert_file=__conf__['webSetting']['certfile'])
            else:
                conn = httplib.HTTPConnection(__conf__['webSetting']['host'],
                                              __conf__['webSetting']['port'])
            auth = base64.encodestring('{0}:{1}'.format(__conf__['webSetting']['username'],
                                                        __conf__['webSetting']['password']).replace('\n', ''))
        elif server == 'builder':
            if __conf__['buildSetting'].get('https'):
                conn = httplib.HTTPSConnection(__conf__['buildSetting']['host'],
                                               __conf__['buildSetting']['port'],
                                               key_file=__conf__['buildSetting']['keyfile'],
                                               cert_file=__conf__['buildSetting']['certfile'])
            else:
                conn = httplib.HTTPConnection(__conf__['buildSetting']['host'],
                                              __conf__['buildSetting']['port'])

            auth = base64.encodestring('{0}:{1}'.format(__conf__['buildSetting']['username'],
                                                        __conf__['buildSetting']['password']).replace('\n', ' '))
        req_body = body
        if compress and body:
            out = StringIO.StringIO()
            with gzip.GzipFile(fileobj=out, mode='w') as f:
                f.write(body)
            req_body = out.getvalue()
        if headers is None:
            headers = {}
        if compress:
            headers.update({'Accept-encoding': 'gzip',
                            'Content-Encoding': 'gzip'})
        headers.update({'Authorization': 'Basic {0} '.format(auth)})
        conn.request(method, url, headers=headers, body=req_body)
        resp = conn.getresponse()
        self.rep_body = resp.read()
        self.rep_status = resp.status
        if self.rep_status == 401:
            print('Login Failed! Exit!')
            raise LoginFailedException()
        self.rep_headers = {k.lower(): v for k, v in resp.getheaders()}
        conn.close()

    def getresponse(self):
        '''get response. if compressed, decompressing firstly
            @return: Response instance
        '''
        compressed = self.rep_headers.get('content-encoding') == 'gzip'
        if compressed:
            buf = StringIO.StringIO(self.rep_body)
            f = gzip.GzipFile(fileobj=buf)
            body = f.read()
            return Response(self.rep_headers, body, self.rep_status)
        else:
            return Response(self.rep_headers, self.rep_body, self.rep_status)
