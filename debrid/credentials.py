import json
from pathlib import Path
import requests
import sqlite3

from debrid.constants import open_source_client_id, client_id_param, credential_url, device_url, new_credentials, \
    client_id, client_secret, code, grant_type, token_url, credentials_file_name, code_param, refresh_token_file_name, \
    refresh_token, grant_type_url, db_path, credentials_scheme, access_token, grant_type_oauth, error_code_bad_token, \
    base_url, user_endpoint, device_code_param


last_credentials = {}

chain_db = sqlite3.connect(db_path)

#################
#   DATABASE    #
#################
# todo: invert return boolean logic
def save_credentials(ci, cs, dc, at, rt):
    # disable old credentials
    if not disable_old_credentials():
        return True

    cursor = chain_db.cursor()

    insert_query = "INSERT INTO credentials(client_id, client_secret, device_code, access_token, refresh_token) " \
                   "VALUES(?,?,?,?,?) "
    errors = False
    try:
        cursor.execute(insert_query, (ci, cs, dc, at, rt))
        chain_db.commit()
    except Exception as e:
        print("Error inserting credentials: {e}")
        errors = True
        chain_db.rollback()
        raise e
    finally:
        cursor.close()
        return errors


def update_token(a_token, r_token):
    cursor = chain_db.cursor()

    update_query = "UPDATE credentials SET access_token = ?, refresh_token = ? WHERE active = 1"
    errors = False
    try:
        cursor.execute(update_query, (a_token, r_token))
        chain_db.commit()
    except Exception as e:
        print("Error inserting tokens: {e}")
        errors = True
        chain_db.rollback()
        raise e
    finally:
        cursor.close()
        return errors


def disable_old_credentials():
    cursor = chain_db.cursor()
    errors = False
    disable_query = "UPDATE credentials SET active = 0"
    try:
        cursor.execute(disable_query)
        chain_db.commit()
    except Exception as e:
        print("Error while disabling old credentials: {e}")
        errors = True
        chain_db.rollback()
        raise e
    finally:
        cursor.close()
        return errors


def disable_credentials(ci):
    cursor = chain_db.cursor()
    errors = False
    disable_query = "UPDATE credentials SET active = 0 WHERE client_id = ?"
    try:
        cursor.execute(disable_query, ci)
        chain_db.commit()
    except Exception as e:
        print("Error while disabling credentials for client_id {ci}: {e}")
        errors = True
        chain_db.rollback()
        raise e
    finally:
        cursor.close()
        return errors


def get_credentials():
    cursor = chain_db.cursor()
    select_query = "SELECT client_id, client_secret, device_code, refresh_token FROM credentials SET WHERE active = 1"
    credentials = None
    try:
        cursor.execute(select_query)
        result = cursor.fetchone()
        credentials = {
            client_id: result[0],
            client_secret: result[1],
            code: result[2],
            refresh_token: result[3]
        }
    except Exception as e:
        print("Error while recovering credentials: {e}")
        raise e
    finally:
        cursor.close()
        return credentials


def close_db():
    if chain_db is not None:
        chain_db.close()

#############
#   LOGIN   #
#############


def get_verification(device_code, cid=open_source_client_id):
    link = credential_url + "?" + client_id_param.format(cid) + "&" + code_param.format(device_code)
    result = requests.get(link)
    return result


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


# checks the current token using a call to /user
def check_token_call():
    global last_credentials
    headers = {"Authorization": "Bearer {}".format(last_credentials["access_token"])}
    result = requests.get(
        user_url,
        headers=headers
    )
    return token_check_and_update(result)


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
