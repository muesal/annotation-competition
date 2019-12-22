'use strict';

const submitButton = document.getElementById("btnSubmit");
const skipButton = document.getElementById("btnSkip");
const tagField = document.getElementById("searchTxt");
const tutorialText = document.getElementById("instruction");
const timemeter = document.getElementById('timemeter');
const timer = document.getElementById('timer');
const score = document.getElementById('score');
const initialTime = 34;


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
    if (tag === 'Castle') {
        advanceState();
        writeToMentionedTags('Castle')
    }
}

function handleSkip(e) {
    e.preventDefault();
    if (tutorialState == 5 || tutorialState == 6){
        advanceState();
    }
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

function highlightImage() {

}

function promptTag() {
    submitButton.disabled = false;
    tagField.disabled = false;
    tutorialText.innerText = "Now you're ready to provide a tag.\n Please enter 'Castle'"

}

function reactToTag() {

    submitButton.disabled = true;
    tagField.disabled = true;
    score.innerText = '3';
    tutorialText.innerText = "Well done!\n You have now received points. \n The tag has been added to the list" +
        "\n Press enter to continue";
}

function explainTimer() {
    setInterval()
    tutorialText.innerText = "The game is on a timer\n" +
        "Wait until the time is up"

}

function promptnewImage() {
    skipButton.disabled = false;
    tutorialText.innerText = "You can request a new image by pressing Start Over"

}

function promptSkip() {
    tutorialText.innerText = "You can also skip an image by pressing Skip";

}

function displayDone() {
    tutorialText.innerText = "Congratulations, you've completed the tutorial!"

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
            promptnewImage();

            break;
        case tutorialState = 6:
            promptSkip();
            break;
        case tutorialState = 7:
            displayDone();
            break;
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
    if (tutorialState == 2 || tutorialState == 5 || tutorialState == 6 || tutorialState == 7) {
        return;
    }

    if (evt.keyCode == 13) {
        advanceState();
    }
};