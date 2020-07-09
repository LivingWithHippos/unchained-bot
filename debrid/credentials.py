import sqlite3
from pathlib import Path

from debrid.constants import open_source_client_id, credential_url, device_url, new_credentials, \
    client_id, client_secret, code, grant_type, token_url, refresh_token, grant_type_url, db_path, access_token, \
    grant_type_oauth, error_code_bad_token, \
    base_url, user_endpoint, credentials_scheme
from utilities.util import make_get, make_post

# create database if missing
if not Path(db_path).is_file():
    with sqlite3.connect(db_path) as my_db:
        creation_cursor = my_db.cursor()
        creation_cursor.execute(credentials_scheme)
        creation_cursor.close()


#################
#   DATABASE    #
#################

def save_credentials(ci, cs, dc, at, rt):
    # disable old credentials
    disable_old_credentials()

    with sqlite3.connect(db_path) as chain_db:
        cursor = chain_db.cursor()

        insert_query = "INSERT INTO credentials(client_id, client_secret, device_code, access_token, refresh_token) " \
                       "VALUES(?,?,?,?,?) "
        errors = False
        try:
            cursor.execute(insert_query, (ci, cs, dc, at, rt))
            chain_db.commit()
        except Exception as e:
            print("Error inserting credentials: ", e)
            errors = True
            chain_db.rollback()
            raise e
        finally:
            cursor.close()
            return errors


def update_token(a_token, r_token):
    with sqlite3.connect(db_path) as chain_db:
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
    with sqlite3.connect(db_path) as chain_db:
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
    with sqlite3.connect(db_path) as chain_db:
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
    with sqlite3.connect(db_path) as chain_db:
        cursor = chain_db.cursor()
        select_query = "SELECT client_id, client_secret, device_code, access_token, refresh_token FROM credentials " \
                       "WHERE active = 1 "
        credentials = None
        try:
            cursor.execute(select_query)
            result = cursor.fetchone()
        except Exception as e:
            print("Error while recovering credentials from database: ", e)
            raise e
        finally:
            cursor.close()
            # if it's the first launch we have no results
            if result is not None:
                credentials = {
                    client_id: result[0],
                    client_secret: result[1],
                    code: result[2],
                    access_token: result[3],
                    refresh_token: result[4]
                }
            return credentials


#############
#   LOGIN   #
#############

def get_auth(cid=open_source_client_id):
    # Your application makes a direct request to the device endpoint, with the query string parameters client_id and
    # new_credentials=yes, and obtains a JSON object with authentication data that will be used for the rest of the
    # process.

    # link = device_url + "?" + client_id_param.format(temp_client_id) + "&" + new_credentials_param
    # result = requests.get(link)
    result = make_get(device_url,
                      params={client_id: cid,
                              new_credentials: "yes"},
                      use_headers=False)

    if result.status_code != 200:
        print("Error logging in, status code ", result.status_code)
        exit(1)
    else:
        return result


def get_verification(device_code, cid=open_source_client_id):
    result = make_get(credential_url,
                      params={client_id: cid,
                              code: device_code},
                      use_headers=False)
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

    result = make_post(token_url, data=data, use_headers=False)

    return result


# return true if the token has been updated
def refresh_current_token():
    credentials = get_credentials()
    result = make_post(token_url,
                       data={
                           client_id: credentials[client_id],
                           client_secret: credentials[client_secret],
                           code: credentials[refresh_token],
                           grant_type: grant_type_oauth,
                       },
                       use_headers=False)

    if result.status_code != 200:
        print("Error refreshing token, status code ", result.status_code)
        return False
    result_json = result.json()
    update_token(result_json[access_token], result_json[refresh_token])
    return True


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


def check_credentials():
    credentials = get_credentials()
    if credentials is None:
        return False
    if "access_token" not in credentials:
        return False

    # data was not null, check if token is valid
    return check_token_call(credentials)


# checks the current token using a call to /user
def check_token_call(credentials):
    user_url = base_url + user_endpoint
    result = make_get(user_url, access_token=credentials["access_token"])
    return token_check_and_update(result)
