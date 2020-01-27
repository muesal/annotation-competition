'use strict';

const submitButton = document.getElementById("btnSubmit");
const skipButton = document.getElementById("btnSkip");
const tagField = document.getElementById("searchTxt");
const tutorialText = document.getElementById("instruction");
const timemeter = document.getElementById('timemeter');
const timer = document.getElementById('timer');
const score = document.getElementById('score');
const img = document.getElementById('tagImage');
const initialTime = 34;
var deadline = 30;


skipButton.addEventListener("click", handleSkip);
submitButton.addEventListener("click", handleSubmit);
tagField.addEventListener("keypress", handleTyping);


var tutorialState = 0;


setInitialSate();


function handleTyping(e) {
}

function handleSubmit(e) {
    e.preventDefault();
    const tag = tagField.value;
    if (tag === 'Castle' || tag === 'castle') {
        advanceState();
        writeToMentionedTags('castle')
    }
}

function handleSkip(e) {
    e.preventDefault();
    console.log("Skip called");
    console.log("Advancing from Skip function");
    clearTags();
    advanceState();
}

function clearTags() {
    document.getElementById("mentionedTags").innerText = "";
}

function setInitialSate() {
    timemeter.value = initialTime;
    timer.innerText = initialTime.toString() + " s";
    tutorialText.innerText = "Welcome to the tutorial for our Annotation Competition!\n Press Enter to continue.";
    submitButton.disabled = true;
    skipButton.disabled = true;
    tagField.disabled = true;
}

function explainPurpose() {
    tutorialText.innerText = "The goal of this game is to crowdsource the tagging of images\n" +
        "To make it more exciting, we give you points!\n Press Enter to continue"
}

function promptTag() {
    submitButton.disabled = false;
    tagField.disabled = false;
    tutorialText.innerText = "Now you're ready to provide a tag.\n Please enter 'castle'"
}

function reactToTag() {

    submitButton.disabled = true;
    tagField.disabled = true;
    score.innerText = '3';
    tutorialText.innerText = "Well done!\n You have now received points. \n The tag has been added to the list" +
        "\n Press enter to continue";
}

function updateTimer() {
    deadline--;
    document.getElementById("timer").innerHTML = deadline + " s";
    document.getElementById("timemeter").value = deadline;
    if (deadline <= 0) {
        document.getElementById('btnSubmit').disabled = true;
        document.getElementById('btnSubmit').value = "Time is up!";
        document.getElementById('btnSkip').value = "Restart";
        document.getElementById('btnSkip').disabled = false;
    }
}

function explainTimer() {
    setInterval(updateTimer, 1000);

    tutorialText.innerText = "The game is on a timer\n" +
        "Wait until the time is up\n" +
        "Then press the \"Restart\" to get a new image"
}

function promptnewImage() {
    skipButton.disabled = false;
    tutorialText.innerText = "You can request a new image by pressing Start Over"
}

function promptSkip() {
    deadline = 60;
    updateTimer();
    clearInterval(timer);
    document.getElementById('btnSkip').value = "Next";

    tutorialText.innerText = "You can also skip an image by pressing Skip";
}

function displayDone() {
    tutorialText.innerText = "Congratulations, you've completed the tutorial!\n" +
        "Press enter to start the game!"
}

function setImgToSkip() {
    img.src = "../static/img/tutorial_2.jpg";
}

function setLastImage() {
    img.src = "../static/img/tutorial_3.jpg";
}

function redirectToClassic() {
    const url = document.getElementById("classicurl").innerText;
    window.location = url;
}


function advanceState() {
    tutorialState++;
    switch (tutorialState) {
        case tutorialState = 1:
            explainPurpose();
            break;
        case tutorialState = 2:
            promptTag();
            break;
        case tutorialState = 3:
            reactToTag();
            break;
        case tutorialState = 4:
            explainTimer();
            break;
        case tutorialState = 5:
            setImgToSkip();
            promptSkip();
            break;
        case tutorialState = 6:
            setLastImage();
            displayDone();
            break;
        case tutorialState = 7:
            redirectToClassic();
        default:
            return;
    }
}


function writeToMentionedTags(tag) {
    const node = document.createElement("LI");                  // Create a <li> node
    const textnode = document.createTextNode(tag.toString());   // Create a text node

    node.appendChild(textnode);                                 // Append the text to <li>
    document.getElementById("mentionedTags").appendChild(node); // Append <li> to <ul> with id="myList"
    mentionedTags.push(tag);
    console.log(mentionedTags);
}

document.onkeydown = function (evt) {
    evt = evt || window.event;
    if (tutorialState == 2 || tutorialState == 5 || tutorialState == 7) {
        return;
    }

    if (evt.keyCode == 13) {
        advanceState();
    }
};