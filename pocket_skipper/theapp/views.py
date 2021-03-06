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
POCKET_OAUTH_ARCHIVE_URL = "https://getpocket.com/v3/send?%s"

POCKET_OAUTH_CONSUMER_KEY = "PUT YOUR OWN"

POCKET_REDIRECT_URL = "http://%s/skipper" # % domain_url

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
    redirect_url = POCKET_REDIRECT_URL % request.get_host()
    data = {"redirect_uri" : redirect_url,
            "consumer_key" : POCKET_OAUTH_CONSUMER_KEY}
    
    content, response = _post(POCKET_OAUTH_REQUEST_URL, data)
    
    pocket_code = dict(urlparse.parse_qsl(response))["code"]
    request.session["pocket_code"] = pocket_code
    auth_url = "https://getpocket.com/auth/authorize?request_token=%s&redirect_uri=%s" % (pocket_code, redirect_url)
    return shortcuts.redirect(auth_url)


def skipper(request):
    #If he has a token in his session use that:
    if "token" in request.session:
        token = request.session["token"]
    
    #Try to reauth the user if there isn't a token:
    else:
        if "pocket_code" not in request.session:
            return shortcuts.redirect("/pocket")
        try:
            pocket_code = request.session["pocket_code"]
            data = {"code" : pocket_code,
                    "consumer_key" : POCKET_OAUTH_CONSUMER_KEY}
            content, response = _post(POCKET_OAUTH_AUTHORIZE_URL, data)
            
            actual_response = dict(urlparse.parse_qsl(response))
            token = actual_response["access_token"]
            username = actual_response["username"]
            
            request.session["token"] = token
        except:
            #Finally fail and ask him to auth:
            return shortcuts.redirect("/pocket")
    
    #Get the item list:
    data = {"access_token" : token,
            "consumer_key" : POCKET_OAUTH_CONSUMER_KEY}
    content, response = _post(POCKET_OAUTH_GET_ALL_URL, data)
    
    #If the status isn't 200, we need to invalidate the cookie and re-auth the user:
    if content["status"] != "200":
        del request.session["token"]
        request.session.modified = True
        return shortcuts.redirect("/pocket")
        
    reading_list_data = json.loads(response)
    reading_list = reading_list_data["list"]
    if reading_list == []:
        reading_list = {}
    
    items = reading_list.values()
    #Sort by date:
    items.sort(cmp=lambda one, two: 1 if one["time_added"] < two["time_added"] else -1)
    
    #Make sure the item has a name, or just show the url if not:
    for item in items:
        item["fool_proof_title"] = item.get("resolved_title", False) or \
                                   item.get("given_title", False) or \
                                   item.get("resolved_url", False) or \
                                   item.get("given_url", "Error: Title or URL was not given")
    
    #Find favicons for each url:
    for item in items:
        try:
            parsed_url = urlparse.urlparse(item["resolved_url"])
            item["favicon_url"] = parsed_url.scheme + r"://" + parsed_url.hostname + "/favicon.ico"
        except:
            pass
    
    t = loader.get_template("list.html")
    c = RequestContext(request, {"items" : items})
    return HttpResponse(t.render(c))


def home(request):
    t = loader.get_template("index.html")
    c = RequestContext(request)
    return HttpResponse(t.render(c))

