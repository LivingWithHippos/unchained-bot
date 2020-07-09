import json
import re

import requests
from bs4 import BeautifulSoup

parsed_file_path = "parsed/parsed_api.json"
api_url = "https://api.real-debrid.com/"


def parse_return_value(value_block):
    schema = value_block.find("div", class_="leswag_schema_placeholder")
    if schema is not None:
        if value_block.find("a", class_="leswag_model_link") is not None:
            # todo: add way to enable table loading
            return "json scheme"

    return_value = str(value_block.find("p", class_="leswag_return_value").contents[0]).strip()
    return return_value


def parse_table(table_block):
    headers = []
    bodies = []
    tab = table_block.find("table", class_="table")
    t_head = tab.find("thead").find_all("th")
    for h in t_head:
        header = str(h.contents[0]).strip()
        if len(header) < 1:
            header = "parameter_type"
        headers.append(header)
    rows = tab.find("tbody").find_all("tr")
    for row in rows:
        values = {}
        index = 0
        fields = row.find_all("td")
        for field in fields:
            values[headers[index]] = str(field.contents[0])
            index += 1
        bodies.append(values)

    return bodies


#####################
#   I START HERE    #
#####################


result = requests.get(api_url)

if result.status_code != 200:
    print("Can't load " + api_url)
    exit(1)

html_doc = result.text
soup = BeautifulSoup(html_doc, 'lxml')

tag = soup.body.find_all("div", class_="leswag_resource")

api_list = []

for t in tag:
    api = {}
    call_type = str(t.find("span").contents[0]).strip()
    api["call_type"] = call_type
    endpoint = str(t.find("h4").contents[1]).strip()
    api["endpoint"] = endpoint
    summary = str(t.find("div", class_="leswag_operation_summary").contents[0]).strip()
    api["summary"] = summary

    info = t.find("div", class_="leswag_operation_full")
    blocks = info.find_all("div", class_="leswag_block")
    for block in blocks:

        if block.find("p", class_="lead") is not None:
            lead = str(block.find("p", class_="lead").contents[0]).strip()
            api["lead"] = lead
            continue

        settings_name = block.find("h5")
        if settings_name is None:
            lead = str(block.contents[0]).strip()
            api["lead"] = lead
            continue
        else:
            settings_name = str(settings_name.contents[0])

        if re.search("Return value", settings_name) is not None:
            rv = parse_return_value(block)
            api["Return values"] = rv
            continue
        if re.search("HTTP error codes", settings_name) is not None:
            error_table = parse_table(block)
            api["error codes"] = error_table
            continue
        if re.search("Parameters", settings_name) is not None:
            parameters_table = parse_table(block)
            api["parameters"] = parameters_table
            continue
    api_list.append(api)

with open(parsed_file_path, 'w') as f:
    json.dump(api_list, f, indent=4)
