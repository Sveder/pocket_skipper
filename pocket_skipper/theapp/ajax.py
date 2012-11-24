import json
import urllib
import httplib2
import traceback

from django.utils import simplejson
from dajaxice.decorators import dajaxice_register

import views

@dajaxice_register
def mark_as_read(request, item_id):
    try:
        actions = [{"action" : "archive",
                    "item_id" : item_id,}]
        action_json = json.dumps(actions)
        
        token = request.session["token"]
        
        data = {"actions" : action_json,
                "access_token" : token,
                "consumer_key" : views.POCKET_OAUTH_CONSUMER_KEY}
        
        headers = {"Content-Type" : "application/x-www-form-urlencoded; charset=UTF-8",
               "X-Accept" : "application/json"}
    
        http = httplib2.Http()
        content, response = http.request(views.POCKET_OAUTH_ARCHIVE_URL % urllib.urlencode(data), "GET", headers=headers)
        if content["status"] != '200':
            raise Exception("Server rejected archive request.")
        
        return simplejson.dumps({'id' : item_id})
    except Exception, e:
        traceback.print_exc()
        return simplejson.dumps({'id' : item_id, "error" : str(e)})
    
    
