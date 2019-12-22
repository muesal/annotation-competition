'use strict';

const submitButton = document.getElementById("btnSubmit");
const skipButton = document.getElementById("btnSkip");
const tagField = document.getElementById("searchTxt");
const tutorialText = document.getElementById("instruction");
const timemeter = document.getElementById('timemeter');
const timer = document.getElementById('timer');


skipButton.addEventListener("click", handleSkip);
submitButton.addEventListener("click", handleSubmit);
tagField.addEventListener("keypress", handleTyping);


var state = 0;


setInitialSate();


function handleTyping(e) {

}

function handleSubmit(e) {
    e.preventDefault();
}

function handleSkip(e) {
    e.preventDefault();
}

function setInitialSate() {
    timemeter.value = 45;
    timer.innerText = "45 s";
    tutorialText.innerText = "Welcome to the tutorial for our Annotation Competition!\n Press Enter to continue."
}

function explainPurpose() {
    tutorialText.innerText="The goal of this game is to crowdsource the tagging of images\n" +
        "To make it more exciting, we give you points!"

}

function highlightImage() {

}

function promptTag() {

}

function setTimeExplanation() {

}


function advanceState() {
    state++;
    switch (state) {
        case state = 1:
            explainPurpose();


        default:
            return;

    }


}


document.onkeydown = function (evt) {
    evt = evt || window.event;
    if (evt.keyCode == 13) {
        advanceState();
    }
};