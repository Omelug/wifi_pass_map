
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
        data: JSON.stringify({ script_name: scriptName, tool_name: toolName }),
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
        body: JSON.stringify({ script_name: scriptName, tool_name: toolName, params: params })
    })
    .then(response => response.json())
    .then(({ status, message }) => status === 'success' ? console.log('Parameters saved successfully') : alert(`Error saving parameters: ${message}`))
    .catch(() => alert('Error saving parameters'));
}
