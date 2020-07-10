credentials_file_name = "user_data/credentials.json"
refresh_token_file_name = "user_data/refresh_token.json"

base_url = "https://api.real-debrid.com/rest/1.0/"
auth_url = "https://api.real-debrid.com/oauth/v2"
grant_type_url = "http://oauth.net/grant_type/device/1.0"

user_endpoint = "user"

device_endpoint = "/device/code"
credentials_endpoint = "/device/credentials"
token_endpoint = "/token"

device_url = auth_url + device_endpoint
credential_url = auth_url + credentials_endpoint
token_url = auth_url + token_endpoint

# remove these
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

# rename these to access_token_param etc. so variables can use these names
access_token = "access_token"
expires_in = "expires_in"
refresh_token = "refresh_token"
token_type = "token_type"

error_code_bad_token = 8

client_id = "client_id"
client_secret = "client_secret"
code = "code"
device_code_param = "device_code"
grant_type = "grant_type"

user_id = "user_id"
credentials_mode = "credentials_mode"
credentials_mode_open = 0
credentials_mode_private = 1

grant_type_oauth = "http://oauth.net/grant_type/device/1.0"

db_path = "user_data/unchaindb"
table_credentials_scheme = "CREATE TABLE credentials(client_id TEXT PRIMARY KEY, client_secret TEXT, device_code TEXT" \
                     ", access_token TEXT, refresh_token TEXT, active NUMERIC DEFAULT 1 )"

table_settings_scheme = "CREATE TABLE settings (id INTEGER PRIMARY KEY, credentials_mode NUMERIC DEFAULT 0, user_id TEXT)"

table_private_token_scheme = "CREATE TABLE private_token (access_token TEXT PRIMARY KEY, active NUMERIC DEFAULT 1 );"
