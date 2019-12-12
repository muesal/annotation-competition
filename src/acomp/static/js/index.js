'use strict';

var score = 0;
var deadline = 60;
var timer = setInterval(updateTimer, 1000);
var mentionedTags = [];
const tagForm = document.getElementById("tagForm");
// TODO: use absolute immutable url
const currentUrl = window.location.href;
const requestUrl = currentUrl + "classic/data";
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
        document.getElementById('btnSubmit').value = "Time is over!";
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
    if (hasAlreadyBeenMentioned(input)) {
        console.log("Tag has already been mentioned");
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

function hasAlreadyBeenMentioned(tag) {
    console.log(mentionedTags.includes(tag));
    return mentionedTags.includes(tag);
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
        const response = await fetch(requestUrl);
        if (response.ok) {
            const json = await response.json();
            console.log('Success:', JSON.stringify(json));
            setTimer(json.timelimit);
            setImg(json.images);
            setScore(json.score);
        } else {
            console.error('Error:', response.statusText); // TODO: notify user
        }
    } catch (err) {
        console.error('Error:', err);
    }
}

async function sendTag(submittedTag) {
    const payload = writeTagToJson(submittedTag);

    try {
        const response = await fetch(requestUrl, {
            method: 'POST',
            body: payload,
            headers: {
                'Content-Type': 'application/json'
            }
        });
        console.log('Sent:', payload);
        if (response.ok) {
            const json = await response.json();
            console.log('Success:', JSON.stringify(json));
            writeToMentionedTags(json.message);
        } else {
            console.error('Error:', response.statusText); // TODO: notify user
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

    document.getElementById("timemeter").value = newTime;

    document.getElementById("timer").innerHTML = deadline + " s";
}
