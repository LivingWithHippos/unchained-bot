import json
import re
from pathlib import Path

from telegram.utils.helpers import escape_markdown

# unchained imports
import debrid.credentials as credentials
from debrid.constants import base_url, magnet, host, credentials_file_name, access_token, user_endpoint, \
    credentials_mode, credentials_mode_open
from utilities.util import make_get, prettify_json, make_post


def get_credentials():
    settings = credentials.get_settings()
    if settings is None:
        credentials.insert_settings()
        settings = credentials.get_settings()
        if settings is None:
            print("Couldn't initialize settings file")
            return
    if settings[credentials_mode] == credentials_mode_open:
        user_credentials = credentials.get_credentials()
        if user_credentials is None:
            print("Couldn't load credentials from db, maybe the user skipped the login procedure?")
        return user_credentials
    # mode is private
    else:
        token = credentials.get_private_token()
        if token is None:
            print("Couldn't load the private token from db, maybe the user didn't set the /private_token")
        return token




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
# fixme: this returns always file_unavailable even when it's available. Error on their side?
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

    download = result.json()

    if "error_code" in download:
        return prettify_json(download)

    markdown = ""
    if "filename" in download:
        markdown += "*" + escape_markdown(download["filename"], version=2) + "*\n"
    if "filesize" in download:
        markdown += "Size: " + escape_markdown(str('%.2f' % (download["filesize"] / (1024 * 1024))),
                                               version=2) + " MB\n"
    if "download" in download:
        markdown += escape_markdown("Download Link:\n" + download["download"] + "\n", version=2)
    if "streamable" in download:
        streamable = "No"
        if download["streamable"] == 1:
            streamable = "Yes"
        markdown += escape_markdown("Streamable: " + streamable + "\n", version=2)

    if len(markdown) > 5:
        return markdown
    else:
        return prettify_json(download)


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
#    STREAMING API    #
#######################

# todo: this endpoint isn't supported without a personal api key. Open source client_id is not allowed

streaming_endpoint = "streaming/"
streaming_url = base_url + streaming_endpoint
rd_id_pattern = "https://real-debrid.com/d/([\w]+)"

# Get streaming links from a streamable source
def api_streaming_transcode(link):
    user_credentials = get_credentials()
    if user_credentials is None:
        print("No credentials were loaded, check if the user has gone through the authentication procedure")
        return None

    rd_id = re.search(rd_id_pattern, link).group(1)
    endpoint = streaming_url + rd_id
    # 'https://real-debrid.com/d/ABFKRBVB5B6YI'

    result = make_get(
        endpoint,
        access_token=user_credentials[access_token])

    streaming_json = result.json()
    markdown = ""

    # todo: complete markdown when you have the personal api key
    if "apple" in streaming_json:
        markdown += "*" + escape_markdown(streaming_json["apple"], version=2) + "*\n"

    markdown += "\n"

    if len(markdown) > 5:
        return markdown
    else:
        return prettify_json(streaming_json)


#######################
#    DOWNLOADS API    #
#######################

downloads_endpoint = "downloads"
downloads_url = base_url + downloads_endpoint


# Get user downloads list
def api_downloads_list(offset=None, page=1, limit=5):
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

    download_json = result.json()
    markdown = ""

    for download in download_json:
        if "filename" in download:
            markdown += "*" + escape_markdown(download["filename"], version=2) + "*\n"
        if "filesize" in download:
            markdown += "Size: " + escape_markdown(str('%.2f' % (download["filesize"] / (1024 * 1024))),
                                                   version=2) + " MB\n"
        if "download" in download:
            markdown += escape_markdown("Download Link:\n" + download["download"] + "\n", version=2)
        if "streamable" in download:
            streamable = "No"
            if download["streamable"] == 1:
                streamable = "Yes"
            markdown += escape_markdown("Streamable: " + streamable + "\n", version=2)

        markdown += "\n"

    if len(markdown) > 5:
        return markdown
    else:
        return prettify_json(download_json)


######################
#    TORRENTS API    #
######################

torrents_endpoint = "torrents"
torrents_url = base_url + torrents_endpoint


# Get user torrents list
def api_torrents_list(offset=None, page=1, limit=5, _filter=None):
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

    torrent_json = result.json()

    markdown = ""
    for torrent in torrent_json:
        if "filename" in torrent:
            markdown += "*" + escape_markdown(torrent["filename"], version=2) + "*\n"
        if "bytes" in torrent:
            markdown += "Size: " + escape_markdown(str('%.2f' % (torrent["bytes"] / (1024 * 1024))),
                                                   version=2) + " MB\n"
        if "progress" in torrent:
            if torrent["progress"] != 100:
                markdown += escape_markdown("Progress: " + str(torrent["progress"]) + "%\n", version=2)
        if "links" in torrent:
            if len(torrent["links"]) > 0:
                markdown += escape_markdown("Download Links (unrestrict these first):\n", version=2)
                for link in torrent["links"]:
                    markdown += escape_markdown(link + "\n", version=2)
        markdown += "\n"

    if len(markdown) > 5:
        return markdown
    else:
        return prettify_json(torrent_json)


# Get available hosts to upload the torrent to.
def api_get_hosts():
    endpoint = torrents_url + "/availableHosts"

    user_credentials = get_credentials()
    if user_credentials is None:
        print("No credentials were loaded, check if the user has gone through the authentication procedure")
        return None

    result = make_get(endpoint, access_token=user_credentials[access_token])

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
