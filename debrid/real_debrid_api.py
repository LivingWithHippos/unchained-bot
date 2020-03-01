import json
import requests
from pathlib import Path

credentials_file_name = "user_data/credentials.json"
refresh_token_file_name = "user_data/refresh_token.json"

base_url = "https://api.real-debrid.com/rest/1.0/"
auth_url = "https://api.real-debrid.com/oauth/v2"
grant_type_url = "http://oauth.net/grant_type/device/1.0"

device_endpoint = "/device/code"
credentials_endpoint = "/device/credentials"
token_endpoint = "/token"

device_url = auth_url + device_endpoint
credential_url = auth_url + credentials_endpoint
token_url = auth_url + token_endpoint

client_id_param = "client_id={}"
code_param = "code={}"
client_secret_param = "client_secret={}"
grant_type_param = "grant_type={}"
new_credentials_param = "new_credentials=yes"

client_id = "client_id"
code = "code"
client_secret = "client_secret"
grant_type = "grant_type"
new_credentials = "new_credentials"
refresh_token = "refresh_token"

sleep_time = 5
open_source_client_id = "X245A4XAIBGVM"

last_credentials = {}

error_code_bad_token = 8


#################
#   LOGIN API   #
#################

# todo: move methods in order

def get_verification(device_code, cid=open_source_client_id):
    link = credential_url + "?" + client_id_param.format(cid) + "&" + code_param.format(device_code)
    result = requests.get(link)
    return result


def add_magnet(magnet, headers):
    data = {"magnet": magnet, "host": "real-debrid.com"}
    result = requests.post(base_url + "torrents/addMagnet", headers=headers, data=data)
    if result.status_code == 400:
        print("Failed adding magnet to RD")
        return False
    elif result.status_code == 401:
        print("Failed adding magnet to RD: Invalid token, to enter authToken, use --token <value>")
        return False
    elif result.status_code == 402:
        print("Failed adding magnet to RD: User not premium")
        return False
    elif result.status_code == 503:
        print("Failed adding magnet to RD: Service not available")
        return False
    else:
        real_id = result.json()["id"]
        select_data = {"files": "all"}
        select_url = base_url + "torrents/selectFiles/" + real_id
        select_result = requests.post(select_url, headers=headers, data=select_data)
        print("Added magnet to Real-Debrid.")
        return True


def get_auth(cid=open_source_client_id):
    # Your application makes a direct request to the device endpoint, with the query string parameters client_id and
    # new_credentials=yes, and obtains a JSON object with authentication data that will be used for the rest of the
    # process.

    # link = device_url + "?" + client_id_param.format(temp_client_id) + "&" + new_credentials_param
    # result = requests.get(link)

    result = requests.get(
        device_url,
        params={client_id: cid,
                new_credentials: "yes"})

    if result.status_code != 200:
        print("Error logging in, status code ", result.status_code)
        exit(1)
    else:
        return result


def get_token(my_client_id, my_client_secret, device_code, my_grant_type=grant_type_url):
    # Using the value of device_code, your application makes a direct POST request to the token endpoint,
    # with the following parameters:
    #
    #     client_id: the value of client_id provided by the call to the credentials endpoint
    #     client_secret: the value of client_secret provided by the call to the credentials endpoint
    #     code: the value of device_code
    #     grant_type: use the value "http://oauth.net/grant_type/device/1.0"

    data = {
        client_id: my_client_id,
        client_secret: my_client_secret,
        code: device_code,
        grant_type: my_grant_type
    }

    result = requests.post(token_url, data=data)

    return result


def check_credentials():
    global last_credentials
    if Path(credentials_file_name).is_file():
        with open(credentials_file_name, 'r') as f:
            data = json.load(f)
            last_credentials = data

        if "access_token" not in last_credentials:
            return False
        # refresh the token if present
        return check_token_call()

    else:
        return False


def save_token_response(token):
    global last_credentials
    last_credentials = token
    write_credentials()


def write_credentials():
    with open(credentials_file_name, 'w') as f:
        json.dump(last_credentials, f, indent=4)


def save_refresh_token(my_client_id, my_client_secret, my_refresh_token, my_grant_type=grant_type_url):
    refresh = {
        client_id: my_client_id,
        client_secret: my_client_secret,
        code: my_refresh_token,
        grant_type: my_grant_type
    }
    write_refresh_token(refresh)


def write_refresh_token(refresh):
    with open(refresh_token_file_name, 'w') as f:
        json.dump(refresh, f, indent=4)


def refresh_current_token():
    global last_credentials
    refresh = None
    if Path(refresh_token_file_name).is_file():
        with open(refresh_token_file_name, 'r') as f:
            refresh = json.load(f)
        if refresh is not None:
            result = requests.post(token_url, data=refresh)
            if result.status_code != 200:
                print("Error refreshing token, status code ", result.status_code)
                return False
            last_credentials = result.json()
            write_credentials()

            refresh[code] = last_credentials[refresh_token]
            write_refresh_token(refresh)

            return True

    else:
        print("Refresh Token file missing")
        return False


#################
#   UTILITIES    #
#################

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


# checks the current token using a call to /user
def check_token_call():
    global last_credentials
    headers = {"Authorization": "Bearer {}".format(last_credentials["access_token"])}
    result = requests.get(
        user_url,
        headers=headers
    )
    return token_check_and_update(result)


# return true if the token was valid or false if it has been updated
def token_check_and_update(response):
    if "error_code" in response.json():
        if response.json()["error_code"] == error_code_bad_token:
            updated_token = refresh_current_token()
            if updated_token:
                return False
            else:
                print("Error while updating the token")
    else:
        return True
    return True


def make_post(endpoint, data, retry=True, use_headers=True):
    if use_headers:
        headers = {"Authorization": "Bearer {}".format(last_credentials["access_token"])}
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
                    headers = {"Authorization": "Bearer {}".format(last_credentials["access_token"])}
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


#################
#   USER API    #
#################

user_endpoint = "user"
user_url = base_url + user_endpoint


def api_user_get():
    global last_credentials
    headers = {"Authorization": "Bearer {}".format(last_credentials["access_token"])}
    result = requests.get(
        user_url,
        headers=headers
    )
    data = result.json()
    return prettify_json(data, _description="Avatar", _link=data["avatar"])


#######################
#   UNRESTRICT API    #
#######################

unrestrict_endpoint = "unrestrict/"
unrestrict_url = base_url + unrestrict_endpoint


# Check if a file is downloadable on the concerned hoster. This request is not requiring authentication.
def api_unrestrict_check(link, password=None):
    if link is None or len(link) < 5:
        return "Command syntax is `/unrestrict  www.your_link.com, please retry"

    endpoint = unrestrict_url + "check"
    data = {"link": link}
    if password is not None:
        data["password"] = password

    result = requests.post(
        endpoint,
        data=data
    )

    check = result.json()

    # if the token has been updated I make the call again
    # todo: as an alternative I call this function again and I return that
    # that would need other checks of course
    # todo: this does not use the token so thereś an error with the call
    # todo: decide if we should send personalized messages for cases
    # if result.status_code == 503:
    #    return "File_unavailable"
    # if result.status_code == 200:
    #    return prettifyJSON(result.json())
    # else:
    #    return "Error : \n" + result.json()

    pretty_data = prettify_json(check)

    if "error_code" in check:
        return pretty_data

    if check["supported"] == 1:
        response = "File is available for download with command /unrestrict [{}]({})\n". \
            format(check["link"], check["link"])
    else:
        response = "File not available on hoster\n"

    return response + pretty_data


# Unrestrict a hoster link and get a new unrestricted link
def api_unrestrict_link(link, password=None, remote=None):

    if link is None or len(link) < 5:
        return "Command syntax is `/unrestrict  www.your_link.com`, please retry"

    endpoint = unrestrict_url + "link"

    data = {"link": link}
    if password is not None:
        data["password"] = password

    if remote is not None:
        data["remote"] = remote

    result = make_post(endpoint, data)

    pretty_data = prettify_json(data)

    if "error_code" in data:
        return pretty_data

    if "download" in result.json():
        output = "[Download link](" + result.json()["download"] + ")\n"
        pretty_data += output
        return output

    return pretty_data


# Unrestrict a hoster folder link and get individual links, returns an empty array if no links found.
def api_unrestrict_folder(link):

    if link is None or len(link) < 5:
        return "Command syntax is `/unrestrict  www.your_link.com`, please retry"

    endpoint = unrestrict_url + "folder"

    data = {"link": link}

    result = make_post(endpoint, data)

    if "error_code" in result.json():
        return result.json()

    if not result.json():
        return "The folder was empty"

    return result.json()


#######################
#    DOWNLOADS API    #
#######################

downloads_endpoint = "downloads"
downloads_url = base_url + downloads_endpoint


# Get user downloads list
def api_downloads_list(offset=None, page=None, limit=3):
    global last_credentials

    endpoint = downloads_url
    headers = {"Authorization": "Bearer {}".format(last_credentials["access_token"])}

    data = {}
    if offset is not None:
        if offset:
            data["offset"] = offset
        else:
            data["offset"] = 0
    else:
        data["offset"] = 0

    if page is not None:
        data["page"] = page

    data["limit"] = limit

    result = requests.get(
        endpoint,
        data=data,
        headers=headers
    )

    if not token_check_and_update(result):
        headers = {"Authorization": "Bearer {}".format(last_credentials["access_token"])}
        result = requests.get(
            unrestrict_url + "link",
            data=data,
            headers=headers
        )

    return prettify_json(result.json())


######################
#    TORRENTS API    #
######################

torrents_endpoint = "torrents"
torrents_url = base_url + torrents_endpoint


# Get user downloads list
def api_torrents_list(offset=0, page=None, limit=3, _filter=None):
    global last_credentials

    endpoint = torrents_url
    headers = {"Authorization": "Bearer {}".format(last_credentials["access_token"])}

    data = {"offset": offset}
    # You can not use both offset and page at the same time, page is prioritzed in case it happens.
    if page is not None:
        data["page"] = page

    data["limit"] = limit
    # "active", list active torrents first
    if _filter is not None:
        data["filter"] = _filter

    result = requests.get(
        endpoint,
        data=data,
        headers=headers
    )

    if not token_check_and_update(result):
        headers = {"Authorization": "Bearer {}".format(last_credentials["access_token"])}
        result = requests.get(
            unrestrict_url + "link",
            data=data,
            headers=headers
        )

    return prettify_json(result.json())


#####################
#   Debrid Class    #
#####################

class DebridApi:
    headers = {"Authorization": "Bearer {}"}
    credentials = {
        "access_token": "",
        "expires_in": "",
        "token_type": "",
        "refresh_token": ""
    }

    def read_credentials(self):

        if Path(credentials_file_name).is_file():
            with open(credentials_file_name, 'r') as f:
                data = json.load(f)
                self.credentials = data
            return True

        else:
            return False

    def save_credentials(self):

        with open(credentials_file_name, 'w') as f:
            json.dump(self.credentials, f, indent=4)

    def save_token(self, token):
        self.credentials["auth_token"] = token
        self.save_credentials()

    def __init__(self):
        a = 1
