// TODO
//'use strict';

var score = 0;
var deadline = 60;
const classicTimeLimit = 20;
resetTimer();
setInterval(displayTimer, 1000);
setInterval(updateTimer, 1000);
var mentionedTags = [];
var tagForm = document.getElementById("tagForm");

function writeToMentionedTags(tag) {
    console.log("Write to tags called");
    var node = document.createElement("LI");                 // Create a <li> node
    var textnode = document.createTextNode(tag.toString());// Create a text node
    node.appendChild(textnode);                              // Append the text to <li>
    document.getElementById("mentionedTags").appendChild(node);     // Append <li> to <ul> with id="myList"
    mentionedTags.push(tag);
    console.log(mentionedTags);
}

function updateScore(delta) {
    score += delta;
    document.getElementById("score").value = score.toString();
}


function handleOutbound(out) { //TODO
    myJson = JSON.stringify(out);
    console.log(myJson);
}

function handleInput(event) {
    event.preventDefault();
    var tag = document.getElementById("searchTxt").value;
    console.log("handleInput called");

    if (!isInputPermissible(tag)) {
        console.log("Input" + tag + " not permissible");
        return;
    }
    writeToMentionedTags(tag);
    sendTag(tag);
}

function displayTimer() {
    console.log("display timer called");
    var remaining = deadline;
    document.getElementById("timer").innerHTML = remaining + " s";
}

function updateTimer() {
    deadline--;
}

function writeTagToJson(tag) {
    var obj = {type: "Tag", content: tag};
    var myJson = JSON.stringify(obj);
    console.log(myJson);
}

function isInputPermissible(input) {
    if (isTimeUp()) {
        console.log("Tag submitted after ");
        return false;
    }
    if (isEmpty()) {
        console.log("Tag is empty");
        return false;
    }
    if (hasAlreadyBeenMentioned()) {
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

function getImageID() {

}

function resetTimer() {
    deadline = classicTimeLimit;
}

function resetTotal(event) {
    resetTags();
    resetTimer();
    getImage();

}

function resetTags() {
    console.log("Resetting tags");
    mentionedTags = [];
    var root = document.getElementById("mentionedTags");
    while (root.firstChild) {
        root.removeChild(root.firstChild);
    }
}

async function getImage() {
    var currentUrl = window.location.href;
    console.log("Current URL: " + currentUrl);
    var requestUrl = currentUrl + "classic/data";
    console.log(requestUrl);
    fetch(requestUrl)
        .then(response => response.json())
        .then(function (jsonResponse) {
            console.log("The thing with the json response");
            console.log(jsonResponse);
            setTimer(jsonResponse.timelimit);
            setImg(jsonResponse.images);
            addPoints(jsonResponse.points);


            console.log("==========");

            // do something with jsonResponse
        });
}


async function sendTag(submittedTag) {
    console.log("Sending tag");
    var currentUrl = window.location.href;
    var requestUrl = currentUrl + "classic/data";

    var tagObject = {
        Type: "Tag",
        Content: submittedTag,
    };
    payload = JSON.stringify(tagObject);
    console.log(payload);
    var data = new FormData();
    data.append("request", payload);

    fetch(requestUrl,
        {
            method: "POST",
            'Content-Type': 'application/json',
    body: payload,
    headers: {
        'Content-Type'
    :
        'application/json'
        // 'Content-Type': 'application/x-www-form-urlencoded',
    }
,
})
.
    then(function (res) {
        return res.json();
    })
        .then(function (data) {
            alert(JSON.stringify(data))
        })

}


function setImg(newImg) {
    console.log("Changing image to " + newImg);
    document.getElementById("tagImage").src = newImg;

}

function setTimer(newTime) {
    deadline = newTime;

}


function getTimelimit() {
}

function getScore() {
}

function hasAlreadyBeenMentioned(tag) {
    console.log(mentionedTags.includes(tag));
    return mentionedTags.includes(tag);
}

function reset() {
    resetTimer();
}

function addPoints(delta) {
    console.log("Received " + delta + " points");
    score += delta;
}

tagForm.addEventListener("reset", resetTotal);
tagForm.addEventListener("submit", handleInput);
