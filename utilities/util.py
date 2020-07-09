import json
import requests


def prettify_json(data, _description=None, _link=None):
    pretty_data = ""
    if _link is not None:
        if _description is None:
            _description = _link
        pretty_data = "[{}]({})".format(_description, _link)

    pretty_data += "```javascript\n" + \
                   json.dumps(data, indent=4) + \
                   "\n```"

    return pretty_data


def get_headers(access_token):
    headers = {"Authorization": "Bearer {}".format(access_token)}
    return headers


# request.post() call helper
# we should just check if access_token is None instead of using use_headers
def make_post(endpoint, data, retry=True, use_headers=True, access_token=None):
    if use_headers:
        headers = get_headers(access_token)
        result = requests.post(
            endpoint,
            data=data,
            headers=headers
        )
    else:
        result = requests.post(
            endpoint,
            data=data
        )

    if retry:
        if result.status_code < 200 or result.status_code > 299:
            result = make_post(endpoint, data, False, use_headers, access_token)

    return result


# request.get() call helper
# todo: check if headers is correct
def make_get(endpoint, params=None, retry=True, use_headers=True, access_token=None):
    if params is None:
        params = {}
    if use_headers:
        headers=get_headers(access_token)
        result = requests.get(
            endpoint,
            params=params,
            headers=headers
        )
    else:
        result = requests.get(
            endpoint,
            params=params
        )

    if retry:
        if result.status_code < 200 or result.status_code > 299:
            result = make_get(endpoint, params, False, use_headers, access_token)

    return result
