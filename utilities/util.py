import json
import requests

from debrid.credentials import token_check_and_update
from debrid.real_debrid_api import unrestrict_url


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


def get_headers():
    global last_credentials
    headers = {"Authorization": "Bearer {}".format(last_credentials["access_token"])}
    return headers


# request.post() call helper
def make_post(endpoint, data, retry=True, use_headers=True):
    if use_headers:
        headers = get_headers()
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
            if use_headers:
                if not token_check_and_update(result):
                    headers = get_headers()
                    result = requests.post(
                        unrestrict_url + "link",
                        data=data,
                        headers=headers
                    )
            else:
                if not token_check_and_update(result):
                    result = requests.post(
                        unrestrict_url + "link",
                        data=data
                    )

    return result


# request.get() call helper
def make_get(endpoint, params=None, retry=True, use_headers=True):
    if params is None:
        params = {}
    if use_headers:
        result = requests.get(
            endpoint,
            params=params,
            headers=get_headers()
        )
    else:
        result = requests.get(
            endpoint,
            params=params
        )

    if retry:
        if result.status_code < 200 or result.status_code > 299:
            if use_headers:
                if not token_check_and_update(result):
                    result = requests.get(
                        unrestrict_url + "link",
                        params=params,
                        headers=get_headers()
                    )
            else:
                if not token_check_and_update(result):
                    result = requests.get(
                        unrestrict_url + "link",
                        params=params
                    )

    return result
