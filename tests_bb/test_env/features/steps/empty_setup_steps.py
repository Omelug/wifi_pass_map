import json
import logging
from io import StringIO

from behave import when, then
from bs4 import BeautifulSoup

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
    assert response_text == f"{context.response.json}", f" response is {context.response.json}"

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