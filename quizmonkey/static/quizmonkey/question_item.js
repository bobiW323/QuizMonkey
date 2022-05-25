function getQuestion() {
    let urlString = document.URL
    let quiz_pk = urlString.split('/')[4];
    let xhr = new XMLHttpRequest()
    xhr.onreadystatechange = function () {
        if (xhr.readyState != 4) return
        updatePage(xhr)
    }
    xhr.open("GET", "/get-question/" + quiz_pk, true)
    xhr.send()
}

function updatePage(xhr) {
    if (xhr.status == 200) {
        let response = JSON.parse(xhr.responseText)
        updateQuestion(response)
        return
    }

    if (xhr.status == 0) {
        displayError("Cannot connect to server")
        return
    }

    if (!xhr.getResponseHeader('content-type') == 'application/json') {
        displayError("Received status=" + xhr.status)
        return
    }

    let response = JSON.parse(xhr.responseText)
    if (response.hasOwnProperty('error')) {
        displayError(response.error)
        return
    }
    displayError(response)
}


function displayError(message) {
    let errorElement = document.getElementById("error")
    errorElement.innerHTML = message
}

function updateQuestion(items) {
    // Removes the old to-do list items
    let list = document.getElementById("question-list")

    for (let i = 0; i < items['questions'].length; i++) {
        let item = items['questions'][i]

        if (document.getElementById('id_question_div_' + item.question_id) == null) {
            let element = document.createElement("div")
            element.id = 'id_question_div_' + item.question_id
            element.className = 'ui basic padded segment'

            let question_text = document.createElement("h4")
            question_text.id = 'question_text_' + item.question_id
            question_text.className = 'ui header'
            question_text.innerHTML = 'Question' + (i + 1) + ':   ' + item.text

            let question_delete = '<form method="post" action="{% url ' + "'delete-question' " + item.question_id + " %}" +
                'style="display: inline-block;">' +
                getCSRFToken() +
                '<button className="btn btn-warning" style="font-family: Futura">delete</button>' +
                '</form>'

            $("#question_text_" + item.question_id).append(question_delete)



                let options = document.createElement('ul')
                options.id = 'question_' + item.question_id + '_options'
                for (let j = 0; j < item.options.length; j++) {
                    let current_option = item.options[j]
                    let option_li = document.createElement("li")
                    if (current_option.is_answer === true) {
                        let color = document.createElement("h")
                        color.style.color = "brown"
                        color.innerHTML +=  (j + 1) + ')    ' + current_option.option
                        option_li.append(color)
                    } else {
                        option_li.innerHTML +=(j + 1) + ')     ' + current_option.option
                    }
                    options.append(option_li)
                }

            element.append(question_text)
            element.append(options)
            list.append(element)
        }
    }
}

function getCSRFToken() {
    let cookies = document.cookie.split(";")
    for (let i = 0; i < cookies.length; i++) {
        let c = cookies[i].trim()
        if (c.startsWith("csrftoken=")) {
            return c.substring("csrftoken=".length, c.length)
        }
    }
    return "unknown"
}