
function clearOutput() {
    $('#live-results').empty();
}

function toggleButtons(disable = true) {
    $('button').prop('disabled', disable);
}

function scrollToBottom(element) {
    element.scrollTop(element.prop('scrollHeight'));
}

function showError(element, message) {
    element.html(message);
    scrollToBottom(element);
    toggleButtons(false);
}


function runTool(scriptName, toolName) {
    let liveResults = $('#live-results');
     toggleButtons(true);

    $.ajax({
        type: 'POST',
        url: '/api/tools',
        contentType: 'application/json',
        data: JSON.stringify({ object_name: scriptName, tool_name: toolName }),
        xhrFields: {
            onprogress: (e) => {
                // Append the entire response text to the liveResults div
                liveResults.html(e.currentTarget.responseText);
                scrollToBottom(liveResults);
            },
            onerror: () => showError(liveResults, 'Error receiving data.')
        },
        success: function (response) {
            liveResults.html(response);
            scrollToBottom(liveResults);
            toggleButtons(false);
        },

        error: () => showError(liveResults, 'Error sending request.')
    });
}

function saveParams(scriptName, toolName) {
    const params = Object.fromEntries(
        [...document.querySelectorAll(`input[id^="${scriptName}_${toolName}_"]`)]
        .map(input => [input.name, input.value])
    );

    fetch('/api/save_params', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ object_name: scriptName, tool_name: toolName, params: params })
    })
    .then(response => response.json())
    .then(({ status, message }) => status === 'success' ? console.log('Parameters saved successfully') : alert(`Error saving parameters: ${message}`))
    .catch(() => alert('Error saving parameters'));
}

function updateLogLevel() {
    const logLevel = document.getElementById('log-level-select').value;

    fetch('/api/set_log_level', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ log_level: logLevel })
    })
    .then(response => response.json())
    .then(({ status, message }) => {
        if (status === 'success') {
            console.log(`Log level updated to ${logLevel}`);
        } else {
            alert(`Error: ${message}`);
        }
    })
    .catch(() => alert('Failed to update log level.'));
}