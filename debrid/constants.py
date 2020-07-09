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

new_credentials = "new_credentials"
magnet = "magnet"
host = "host"

sleep_time = 5
open_source_client_id = "X245A4XAIBGVM"

access_token = "access_token"
expires_in = "expires_in"
refresh_token = "refresh_token"
token_type = "token_type"

client_id = "client_id"
client_secret = "client_secret"
code = "code"
device_code = "device_code"
grant_type = "grant_type"

db_path = "user_data/unchaindb"
credentials_scheme = "CREATE TABLE credentials(client_id TEXT PRIMARY KEY, client_secret TEXT, device_code TEXT" \
                     ", access_token TEXT, refresh_token TEXT, active NUMERIC DEFAULT 1 ) "
