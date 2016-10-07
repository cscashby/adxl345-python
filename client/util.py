import urllib

def urlPost(url, params=None):
    if params:
        f = urllib.urlopen(url, urllib.urlencode(params))
    else:
        f = urllib.urlopen(url)
    out = f.read()
    return out