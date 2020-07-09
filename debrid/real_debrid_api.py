import json
from pathlib import Path

import requests

# unchained imports
import debrid.credentials as credentials
from debrid.constants import base_url, magnet, host, credentials_file_name, access_token, user_endpoint
from utilities.util import make_get, prettify_json, make_post


def get_credentials():
    user_credentials = None
    user_credentials = credentials.get_credentials()
    if user_credentials is None:
        print("Couldn't load credentials from db, maybe the user skipped the login procedure?")

    return user_credentials


# todo: refactor the api calls, maybe with the class, so that the credentials recovery and check doesn't need to be
#  added to every api call function

#################
#   USER API    #
#################

user_url = base_url + user_endpoint


def api_user_get():
    # todo: this method is used to check for status so we initialize user_credentials here
    user_credentials = get_credentials()
    if user_credentials is None:
        print("No credentials were loaded, check if the user has gone through the authentication procedure")
        return None
    result = make_get(user_url, access_token=user_credentials[access_token])
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

    result = make_post(
        endpoint,
        data,
        use_headers=False)

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

    user_credentials = get_credentials()
    if user_credentials is None:
        print("No credentials were loaded, check if the user has gone through the authentication procedure")
        return None
    result = make_post(endpoint, data, access_token=user_credentials[access_token])

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

    user_credentials = get_credentials()
    if user_credentials is None:
        print("No credentials were loaded, check if the user has gone through the authentication procedure")
        return None
    result = make_post(endpoint, data, access_token=user_credentials[access_token])

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
def api_downloads_list(offset=None, page=1, limit=3):
    endpoint = downloads_url

    data = {}
    if offset is not None:
        if offset:
            data["offset"] = offset
        else:
            data["offset"] = 0
    else:
        data["offset"] = 0

    data["page"] = page
    data["limit"] = limit

    user_credentials = get_credentials()
    if user_credentials is None:
        print("No credentials were loaded, check if the user has gone through the authentication procedure")
        return None
    result = make_get(
        endpoint,
        params=data,
        access_token=user_credentials[access_token])

    return prettify_json(result.json())


######################
#    TORRENTS API    #
######################

torrents_endpoint = "torrents"
torrents_url = base_url + torrents_endpoint


# Get user downloads list
def api_torrents_list(offset=None, page=1, limit=3, _filter=None):
    endpoint = torrents_url

    params = {"page": page}
    # You can not use both offset and page at the same time, page is prioritized in case it happens.
    if offset is not None:
        params["offset"] = offset

    params["limit"] = limit
    # "active", list active torrents first
    if _filter is not None:
        params["filter"] = _filter

    user_credentials = get_credentials()
    if user_credentials is None:
        print("No credentials were loaded, check if the user has gone through the authentication procedure")
        return None
    result = make_get(endpoint, params, access_token=user_credentials[access_token])

    return result.json()


# Get available hosts to upload the torrent to.
def api_get_hosts():
    endpoint = torrents_url + "/availableHosts"

    result = make_get(endpoint, use_headers=False)

    if result.status_code != 200:
        print(result.json())
        return []

    return result.json()


# Add a magnet link to download, return a 201 HTTP code.
def api_add_magnet(_magnet):
    endpoint = torrents_url + "/addMagnet"
    available_hosts = api_get_hosts()
    if not available_hosts:
        return "Error checking available hosts. Check logs and/or retry."
    data = {magnet: _magnet, host: available_hosts[0][host]}

    user_credentials = get_credentials()
    if user_credentials is None:
        print("No credentials were loaded, check if the user has gone through the authentication procedure")
        return None

    result = make_post(endpoint, data, access_token=user_credentials[access_token])

    if result.status_code != 201:
        return prettify_json(result.json())

    # starts the torrent with all the files
    add_result = api_select_files(result.json()["id"])
    if add_result.status_code == 204:
        return "Magnet Successfully Added."
    else:
        return "Issue with magnet, http status code {}.".format(add_result.status_code)


# Select files of a torrent to start it, do not return anything with a 204 HTTP code.
def api_select_files(_id, select="all"):
    endpoint = torrents_url + "/selectFiles/{}".format(_id)
    data = {"files": select}
    user_credentials = get_credentials()
    result = make_post(endpoint, data, access_token=user_credentials[access_token])

    return result


#####################
#   Debrid Class    #
#####################

# todo: edit this class to get the credentials from the db and orchestrate the api calls
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
