import re

def cam_id_from_url(url):
    # counts number of '/' https:// xxx / yyy / stream_id [/?] ...
    found = re.findall(".+//(?:[^/]+/){2}([^/?]+).*", url)

    if(found != None and len(found) == 1):
        return found[0]
    else:
        return None