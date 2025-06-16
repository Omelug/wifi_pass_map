from behave import when, then

@when('Client {method} "{path}"')
def step_impl(context, method, path):
    method = method.lower()
    client_method = getattr(context.client, method)
    context.response = client_method(path)

@then('web code is {code_status}')
def step_impl(context,code_status):
    assert context.response.status_code == int(code_status)

@then('html "{tag}" "{text}" is visible')
def step_impl(context, tag, text):
    html = context.response.get_data(as_text=True)
    assert f"<{tag}" in html and text in html, f'{tag} with text "{text}" not found in response'
