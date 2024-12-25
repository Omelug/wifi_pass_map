
function clearOutput() {
    $('#live-results').empty();
}

function disableAllButtons() {
    $('button').prop('disabled', true);
}

function enableAllButtons() {
    $('button').prop('disabled', false);
}

function scrollToBottom(element) {
    const height = element.prop('scrollHeight');
    element.scrollTop(height);
}

function runTool(scriptName) {
    let liveResults = $('#live-results');

    disableAllButtons();

    $.ajax({
        type: 'POST',
        url: '/api/tools',
        contentType: 'application/json',
        data: JSON.stringify({ script_name: scriptName }),
        xhrFields: {
            onprogress: function (e) {
                // Append the entire response text to the liveResults div
                liveResults.html(e.currentTarget.responseText);
                scrollToBottom(liveResults);
            },
            onerror: function (xhr, status, error) {
                console.error('Error receiving data:', error);
                liveResults.html('Error receiving data. Please try again.');

                scrollToBottom(liveResults);
            }
        },
        success: function (response) {
            // Display the final response in the liveResults div
            liveResults.html(response);
            scrollToBottom(liveResults);
            enableAllButtons();
        },
        error: function (xhr, status, error) {
            console.error('Error sending request:', error);
            liveResults.html('Error sending request. Please try again.');

            scrollToBottom(liveResults);
            enableAllButtons();
        }
    });
}
/*
function uploadFile(event) {
    var file = event.target.files[0];
    if (file) {
        var formData = new FormData();
        formData.append('file', file);

        $.ajax({
            url: '/api/pot_upload',
            type: 'POST',
            data: formData,
            contentType: false,
            processData: false,
            success: function (response) {
                if (response.status === "success") {
                    runTool('manual_pot');
                } else {
                    $('#live-results').html(response.message);
                    enableAllButtons();
                }
            },
            error: function (xhr, status, error) {
                console.error('Error uploading file:', error);
                $('#live-results').html('Error uploading file. Please try again.');
                enableAllButtons();
            }
        });
    }
}*/

