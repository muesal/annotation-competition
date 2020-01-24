'use strict';

var score = 0;
var deadline = 60;
var timer = setInterval(updateTimer, 1000);
var mentionedTags = [];
const csrf_token = document.getElementById("csrf_token");
const tagForm = document.getElementById("tagForm");
tagForm.addEventListener("reset", resetTotal);
tagForm.addEventListener("submit", handleInput);

resetTotal();

function writeToMentionedTags(tag) {
    const node = document.createElement("LI");                  // Create a <li> node
    const textnode = document.createTextNode(tag.toString());   // Create a text node

    node.appendChild(textnode);                                 // Append the text to <li>
    document.getElementById("mentionedTags").appendChild(node); // Append <li> to <ul> with id="myList"
    mentionedTags.push(tag);
    console.log(mentionedTags);
}

function handleInput(event) {
    const tag = document.getElementById("searchTxt").value;
    event.preventDefault();

    if (!isInputPermissible(tag)) {
        console.log("Input" + tag + " not permissible");
        return;
    }
    sendTag(tag);
    document.getElementById("searchTxt").value = "";
}

function updateTimer() {
    deadline--;
    document.getElementById("timer").innerHTML = deadline + " s";
    document.getElementById("timemeter").value = deadline;
    if (deadline <= 0) {
        clearInterval(timer);
        document.getElementById('btnSubmit').disabled = true;
        document.getElementById('btnSubmit').value = "Time is up!";
        document.getElementById('btnSkip').value = "Restart";
    }
}

function isInputPermissible(input) {
    if (isTimeUp()) {
        console.log("Tag submitted after ");
        return false;
    }
    if (isEmpty(input)) {
        console.log("Tag is empty");
        return false;
    }
    return true;
}

function isTimeUp() {
    return deadline < 0;
}

function isEmpty(input) {
    return input === "";
}

function resetTotal(event) {
    resetTags();
    getClassicData();
    document.getElementById('btnSubmit').disabled = false;
    document.getElementById('btnSubmit').value = "Submit";
    document.getElementById('btnSkip').value = "Skip";
}

function resetTags() {
    console.log("Resetting tags");
    mentionedTags = [];
    const root = document.getElementById("mentionedTags");
    while (root.firstChild) {
        root.removeChild(root.firstChild);
    }
}

async function getClassicData() {
    try {
        const response = await fetch(tagForm.dataset.datauri);
        if (response.ok) {
            const json = await response.json();
            console.log('Success:', JSON.stringify(json));
            for (var i = 0; ; i++) {
                var current = json.forbidden[i]
                if (current === undefined) {
                    break;
                }
                writeToMentionedTags(current);
            }
            setTimer(json.timelimit);
            setImg(json.images);
            setScore(json.score);
        } else {
            console.error('Error:', response.statusText);
            notifyUser(response.statusText);

        }
    } catch (err) {
        console.error('Error:', err);
    }
}

async function sendTag(submittedTag) {
    const payload = writeTagToJson(submittedTag);

    try {
        const response = await fetch(tagForm.dataset.datauri, {
            method: 'POST',
            body: payload,
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrf_token.value,
            }
        });
        console.log('Sent:', payload);
        if (response.ok) {
            const json = await response.json();
            console.log('Success:', JSON.stringify(json));
            if (json.accepted === 1) {
                writeToMentionedTags(json.message);
            } else {
                notifyUser(json.message)
            }
        } else {
            console.error('Error:', response.statusText);
            notifyUser(response.statusText);
        }
    } catch (err) {
        console.error('Error:', err);
    }
}

function writeTagToJson(mytag) {
    const obj = {tag: mytag};
    const myJson = JSON.stringify(obj);
    return myJson;
}

function setImg(newImg) {
    console.log("Changing image to " + newImg);
    document.getElementById("tagImage").src = newImg;
}

function setScore(score) {
    document.getElementById("score").value = score.toString();
}

function setTimer(newTime) {
    deadline = newTime;
    clearInterval(timer);
    timer = setInterval(updateTimer, 1000);
    var timerMeter = document.getElementById("timemeter");

    document.getElementById("timemeter").value = newTime;
    timerMeter.max = newTime;
    timerMeter.low = newTime / 4;
    timerMeter.high = timerMeter / 2;
    timerMeter.optimum = (3 * timerMeter) / 4;

    document.getElementById("timer").innerHTML = deadline + " s";
}


function notifyUser(msg) {
    const snackbarContainer = document.querySelector('#demo-toast-example');
    const data = {message: msg};
    snackbarContainer.MaterialSnackbar.showSnackbar(data);
}
