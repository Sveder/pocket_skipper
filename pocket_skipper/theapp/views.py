import json
import pprint
import urllib
import httplib2
import urlparse
import traceback

import django.shortcuts as shortcuts
from django.template import RequestContext, Context, loader
from django.http import HttpResponse, Http404, HttpResponseBadRequest


POCKET_OAUTH_REQUEST_URL = "https://getpocket.com/v3/oauth/request"
POCKET_OAUTH_AUTHORIZE_URL = "https://getpocket.com/v3/oauth/authorize"
POCKET_OAUTH_GET_ALL_URL = "https://getpocket.com/v3/get"
POCKET_OAUTH_ARCHIVE_URL = "https://getpocket.com/v3/send?actions=%s&access_token=%s&consumer_key=%s"
                            # % (json_url_encoded_action, access_token, consumer_key)

POCKET_OAUTH_CONSUMER_KEY = "PUT YOUR OWN"

POCKET_SKIPPER_BASE_URL = "pocket_skipper"
POCKET_REDIRECT_URL = "http://%s/" + POCKET_SKIPPER_BASE_URL + "/skipper" # % domain_url

g_pocket_code = None

def _log(message, _pprint=False, _traceback=False):
    if _pprint:
        pprint.pprint(message)
    else:
        print message
    
    if _traceback:
        traceback.print_exc()
        
def _post(url, data):
    headers = {"Content-Type" : "application/x-www-form-urlencoded; charset=UTF-8",
               "X-Accept" : "application/x-www-form-urlencoded"}
    
    http = httplib2.Http()
    content, response = http.request(url, "POST", urllib.urlencode(data), headers=headers)
    return content, response


def landing(request):
    global g_pocket_code
    redirect_url = POCKET_REDIRECT_URL % request.get_host()
    data = {"redirect_uri" : redirect_url,
            "consumer_key" : POCKET_OAUTH_CONSUMER_KEY}
    
    content, response = _post(POCKET_OAUTH_REQUEST_URL, data)
    g_pocket_code = dict(urlparse.parse_qsl(response))["code"]
    
    auth_url = "https://getpocket.com/auth/authorize?request_token=%s&redirect_uri=%s" % (g_pocket_code, redirect_url)
    return shortcuts.redirect(auth_url)

def skipper(request):
    if "token" in request.session:
        token = request.session["token"]
    
    else:
        try:
            data = {"code" : g_pocket_code,
                    "consumer_key" : POCKET_OAUTH_CONSUMER_KEY}
            content, response = _post(POCKET_OAUTH_AUTHORIZE_URL, data)
            
            actual_response = dict(urlparse.parse_qsl(response))
            token = actual_response["access_token"]
            username = actual_response["username"]
            
            request.session["token"] = token
        except:   
            return shortcuts.redirect("/pocket")
    
    data = {"access_token" : token,
            "consumer_key" : POCKET_OAUTH_CONSUMER_KEY}
    content, response = _post(POCKET_OAUTH_GET_ALL_URL, data)
    
    reading_list_data = json.loads(response)
    reading_list = reading_list_data["list"]
    
    html = ""
    
    for item in reading_list.values():
        actions = [{"action" : "archive",
                    "item_id" : item["item_id"],}]
        action_json = json.dumps(actions)
        
        archive_url = POCKET_OAUTH_ARCHIVE_URL % (action_json, token, POCKET_OAUTH_CONSUMER_KEY)
        html += "<a href='%s'>%s</a> -- <a href='%s'>Mark As Read</a><br>" % (item["given_url"], item["given_title"], archive_url)
    
    
    return HttpResponse(html)