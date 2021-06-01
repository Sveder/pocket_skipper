import json
import pprint
import traceback
import urllib.request, urllib.parse, urllib.error

import requests
import django.shortcuts as shortcuts
from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext, Context, loader
from django.http import HttpResponse, Http404, HttpResponseBadRequest


POCKET_OAUTH_REQUEST_URL = "https://getpocket.com/v3/oauth/request"
POCKET_OAUTH_AUTHORIZE_URL = "https://getpocket.com/v3/oauth/authorize"
POCKET_OAUTH_GET_ALL_URL = "https://getpocket.com/v3/get"
POCKET_OAUTH_ARCHIVE_URL = "https://getpocket.com/v3/send?%s"

POCKET_OAUTH_CONSUMER_KEY = "11798-8b31a6c8596a31af57059a0e"

POCKET_REDIRECT_URL = "http://%s/skipper" # % domain_url


def _log(message, _pprint=False, _traceback=False):
    if _pprint:
        pprint.pprint(message)
    else:
        print(message)
    
    if _traceback:
        traceback.print_exc()


def _post(url, data):
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    }

    res = requests.post(
        url,
        data=data,
        headers=headers
    )
    _log('-->' + res.text)
    _log(res.status_code)
    return res.text, res.status_code


def landing(request):
    redirect_url = POCKET_REDIRECT_URL % request.get_host()
    data = {
        "redirect_uri": redirect_url,
        "consumer_key": POCKET_OAUTH_CONSUMER_KEY
    }
    
    response, status_code = _post(POCKET_OAUTH_REQUEST_URL, data)

    pocket_code = urllib.parse.parse_qs(response)['code'][0]
    request.session["pocket_code"] = pocket_code

    auth_url = "https://getpocket.com/auth/authorize?" \
               "request_token=%s&redirect_uri=%s" % (pocket_code, redirect_url)
    return shortcuts.redirect(auth_url)


def skipper(request):
    # If he has a token in his session use that:
    if "token" in request.session:
        token = request.session["token"]
    
    # Try to reauth the user if there isn't a token:
    else:
        if "pocket_code" not in request.session:
            return shortcuts.redirect("/pocket")

        try:
            pocket_code = request.session["pocket_code"]
            data = {
                "code": pocket_code,
                "consumer_key": POCKET_OAUTH_CONSUMER_KEY
            }
            response, _ = _post(POCKET_OAUTH_AUTHORIZE_URL, data)

            parsed_res = urllib.parse.parse_qs(response)
            token = parsed_res["access_token"][0]
            username = parsed_res["username"][0]
            
            request.session["token"] = token

        except:
            # Finally fail and ask him to auth:
            return shortcuts.redirect("/pocket")
    
    # Get the item list:
    data = {
        "access_token": token,
        "consumer_key": POCKET_OAUTH_CONSUMER_KEY
    }
    response, status_code = _post(POCKET_OAUTH_GET_ALL_URL, data)
    
    # If the status isn't 200, we need to invalidate the cookie and re-auth the user:
    if status_code != 200:
        del request.session["token"]
        request.session.modified = True
        return shortcuts.redirect("/pocket")
        
    reading_list_data = json.loads(response)
    reading_list = reading_list_data["list"]
    if reading_list == []:
        reading_list = {}
    
    items = list(reading_list.values())

    # Sort by date:
    items.sort(key=lambda x: x["time_added"])
    items.reverse()
    
    # Make sure the item has a name, or just show the url if not:
    for item in items:
        item["fool_proof_title"] = item.get("resolved_title", False) or \
                                   item.get("given_title", False) or \
                                   item.get("resolved_url", False) or \
                                   item.get("given_url", "Error: Title or URL was not given")
    
    # Find favicons for each url:
    for item in items:
        try:
            parsed_url = urllib.parse.urlparse(item["resolved_url"])
            item["favicon_url"] = parsed_url.scheme + r"://" + parsed_url.hostname + "/favicon.ico"

        except:
            pass
    
    t = loader.get_template("list.html")
    return HttpResponse(t.render({"items": items}))


def home(_):
    t = loader.get_template("index.html")
    return HttpResponse(t.render())


@csrf_exempt
def mark_as_read(request):
    if request.method != 'POST':
        raise Exception('Only post is supported.')

    item_id = request.POST.get('item_id')
    if not item_id:
        raise Exception('item_id must be provided.')

    try:
        actions = [{
            "action": "archive",
            "item_id": item_id
        }]
        action_json = json.dumps(actions)

        token = request.session["token"]

        data = {
            "actions": action_json,
            "access_token": token,
            "consumer_key": POCKET_OAUTH_CONSUMER_KEY
        }

        response, status_code = _post(POCKET_OAUTH_ARCHIVE_URL, data=data)
        if status_code != 200:
            raise Exception("Server rejected archive request.")

        return HttpResponse(json.dumps({'id': item_id}))

    except Exception as e:
        traceback.print_exc()
        return HttpResponse(json.dumps({'id': item_id, "error": str(e)}))
