import re

def cam_id_from_url(url):
    searchRes = re.search(".+/([0-9]+)/.+", url)

    if(searchRes != None and len(searchRes.groups()) == 1):
        return searchRes.groups(0)[0]
    else:
        return None