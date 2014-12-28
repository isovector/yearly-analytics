#!/usr/bin/python2.6
import os.path
import json
import urllib2
import urllib
import urlparse
import BaseHTTPServer
import webbrowser
import time
import datetime
from collections import defaultdict


NAME = "tino"

APP_ID = "1512576815698643"
APP_SECRET = "6b61bba817c1fc44e3fb2696da004119"
ENDPOINT = 'graph.facebook.com'
REDIRECT_URI = 'http://localhost:8080/'
ACCESS_TOKEN = None
LOCAL_FILE = '.fb_access_token'
YEAR = 2014

def get_url(path, args=None):
    args = args or {}
    if ACCESS_TOKEN:
        args['access_token'] = ACCESS_TOKEN
    if 'access_token' in args or 'client_secret' in args:
        endpoint = "https://"+ENDPOINT
    else:
        endpoint = "http://"+ENDPOINT
    return endpoint+path+'?'+urllib.urlencode(args)

def get(path, args=None):
    return urllib2.urlopen(get_url(path, args=args)).read()

def getPage(path):
    return urllib2.urlopen(path).read()

class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def do_GET(self):
        global ACCESS_TOKEN
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        code = urlparse.parse_qs(urlparse.urlparse(self.path).query).get('code')
        code = code[0] if code else None
        if code is None:
            self.wfile.write("Sorry, authentication failed.")
            sys.exit(1)
        response = get('/oauth/access_token', {'client_id':APP_ID,
                                               'redirect_uri':REDIRECT_URI,
                                               'client_secret':APP_SECRET,
                                               'code':code})
        ACCESS_TOKEN = urlparse.parse_qs(response)['access_token'][0]
        open(LOCAL_FILE,'w').write(ACCESS_TOKEN)
        self.wfile.write("You have successfully logged in to facebook. "
                         "You can close this window now.")


totalSends = 0
totalRecvs = 0
def msgSent(convo, who):
    global totalSends, totalRecvs
    if convo == who:
        totalRecvs += 1
    else:
        totalSends += 1

def handleComments(convo, data, page):
    print "----%s: %d----" % (convo, page)
    for item in data["data"]:
        msgSent(convo, item["from"]["name"])
    time.sleep(1)
    if "paging" in data and "next" in data["paging"]:
        handleComments(convo, json.loads(getPage(data["paging"]["next"])), page + 1)

def handleStream(stream):
    global NAME
    global totalSends, totalRecvs
    convo = stream["to"]["data"]
    for person in convo:
        if person["name"] != NAME:
            convo = person["name"]
            break

    path = "results/%s.txt" % convo
    if not os.path.exists(path):
        handleComments(convo, stream["comments"], 1)
        with open(path, 'w') as f:
            f.write("sends: %d\n" % totalSends)
            f.write("recvs: %d\n" % totalRecvs)
    totalSends = 0
    totalRecvs = 0



if __name__ == '__main__':
    if not os.path.exists(LOCAL_FILE):
        print "Logging you in to facebook..."
        webbrowser.open(get_url('/oauth/authorize',
                                {'client_id':APP_ID,
                                 'redirect_uri':REDIRECT_URI,
                                 'scope':'read_inbox'}))

        httpd = BaseHTTPServer.HTTPServer(('127.0.0.1', 8080), RequestHandler)
        while ACCESS_TOKEN is None:
            httpd.handle_request()
    else:
        ACCESS_TOKEN = open(LOCAL_FILE).read()


    timestamp = int(time.mktime(datetime.datetime.strptime("01/01/%d" % YEAR, "%d/%m/%Y").timetuple()))
    #try:
    data = json.loads(get('/me/inbox', {"fields": 'comments.since(%d){from},to' % timestamp }))
    for stream in data["data"]:
        handleStream(stream)
    #except:
    #    pass
    #finally:
    print(repr(send))
    print(repr(recv))
    print("total sends: %d" % totalSends)
    print("total recvs: %d" % totalRecvs)
