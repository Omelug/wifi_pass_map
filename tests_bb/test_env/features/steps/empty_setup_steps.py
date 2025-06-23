import configparser
import json
import logging
import os
from io import StringIO
from unittest.mock import patch

from behave import given, when, then
from bs4 import BeautifulSoup

from map_app.source_core.manager import tool_list


@when('Client {method} "{path}"')
def step_impl(context, method, path):
    method = method.lower()
    client_method = getattr(context.client, method)
    context.response = client_method(path)

@then('web code is {code_status}')
def step_impl(context,code_status):
    assert context.response.status_code == int(code_status)

@then('web response is {response_text}')
def step_impl(context, response_text):
    import json
    expected = json.loads(response_text.replace("'", '"'))
    actual = context.response.get_json()
    assert expected == actual, f" response is {actual}"

@then('html "{tag}" "{text}" is visible')
def step_impl(context, tag, text):
    html = context.response.get_data(as_text=True)
    assert f"<{tag}" in html and text in html, f'{tag} with text "{text}" not found in response'

# ------------- TOOLS -----------
@then('every config has label, value input, and description')
def step_impl(context):
    html = context.response.get_data(as_text=True)
    soup = BeautifulSoup(html, "html.parser")
    for container in soup.select('.input-container'):
        labels = container.find_all('label')

        assert len(labels) >= 2, "Not enough labels in input-container"
        assert labels[0].get_text(strip=True), "First label is empty"
        assert container.find('input'), "No input in input-container"
        assert labels[1].get_text(strip=True), "Description label is empty"



@when('API POST "{path}" with data "{data_str}"')
def step_impl(context, path, data_str):
    data = json.loads(data_str)
    context.response = context.client.post(path, data=json.dumps(data), content_type='application/json')

@then('log contains "{message}"')
def step_impl(context, message):
    logs = context.log_stream.getvalue()
    assert message in logs, f'Log does not contain: {message}'


# ----- DEBUG tests --------
@then('print app logger info')
def step_impl(context):
    logger = context.app.logger
    print("Logger name:", logger.name)
    print("Logger level:", logging.getLevelName(logger.level))
    print("Handlers:", logger.handlers)
    print("Propagate:", logger.propagate)

# ------ TOOLS ----------

@then('web response contains "{text}"')
def step_impl(context, text):
    assert text in context.response.get_data(as_text=True), f"{context.response.get_data(as_text=True)}"

"""
@given('tool "{tool_name}" exists with "plugin")
def step_impl(context, tool_name, tool):
    def dummy_run_fun():
        pass
    dummy_tools = {
        tool_name: {
            "tool1": {"run_fun": dummy_run_fun}
        }
    }
    patcher = patch('map_app.source_core.manager.tool_list', return_value=dummy_tools)
    context.tool_list_patcher = patcher.start()
    context.add_cleanup(patcher.stop)

@given('tool "{tool_name}" exists without run_fun')
def step_impl(context, tool_name):
    dummy_tools = {
        tool_name: {
            "tool1": {}
        }
    }
    patcher = patch('map_app.source_core.manager.tool_list', return_value=dummy_tools)
    context.tool_list_patcher = patcher.start()
    context.add_cleanup(patcher.stop)
"""

# ------------------ BACKUP -------------------------

@given('config "{config_file_name}" "{config_name}" is "{param_value}"')
def step_impl(context, config_file_name, config_name, param_value):
    config_path = os.path.join(os.path.dirname(__file__), f'../src/map_app/sources/{config_file_name}.ini')
    config_path = os.path.abspath(config_path)
    assert os.path.isfile(config_path), f"Config file not found at {config_path}"

    config = configparser.ConfigParser()
    config.read(config_path)
    assert config_name in config, f"Section '{config_name}' not found in {config_file_name}.ini"
    found = any(value == param_value for value in config[config_name].values())
    assert found, f"No value '{param_value}' found in section '{config_name}' of {config_file_name}.ini"

@when('tool run "{object_name}" "{tool_name}"')
def step_impl(context, object_name, tool_name):
    tools = tool_list(add_class=True)
    func = tools[object_name][tool_name].get("run_fun", None)
    assert func is not None
    func()

@then('root "{folder}" "{f_type}" exists')
def step_impl(context, folder, f_type):
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..', folder))
    if f_type == "folder":
        assert os.path.isdir(path), f'Folder not found: {path}'
    elif f_type == "file":
        assert os.path.isfile(path), f'File not found: {path}'
    else:
        raise ValueError(f'Unknown type: {f_type}')

@then('in root "{parent}" is "{f_type}" "{name}"')
def step_impl(context, parent, f_type, name):
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..', parent, name))
    if f_type == "folder":
        assert os.path.isdir(path), f'Folder not found: {path}'
    elif f_type == "file":
        assert os.path.isfile(path), f'File not found: {path}'
    else:
        raise ValueError(f'Unknown type: {f_type}')