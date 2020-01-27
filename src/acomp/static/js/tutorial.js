'use strict';

const img = document.getElementById('tagImage');
const initialTime = 34;
const nextButton = document.getElementById("btnNext");
const score = document.getElementById('score');
const skipButton = document.getElementById("btnSkip");
const snackbar = document.getElementById('snackbar');
const submitButton = document.getElementById("btnSubmit");
const startButton = document.getElementById("btnStart");
const tagField = document.getElementById("searchTxt");
const tagForm = document.getElementById("tagForm");
const timemeter = document.getElementById('timemeter');
const timer = document.getElementById('timer');
var deadline = 30;

skipButton.addEventListener("click", handleSkip);
submitButton.addEventListener("click", handleSubmit);
startButton.addEventListener("click", setInitialSate);
nextButton.addEventListener("click", advanceState);

var tutorialState = 0;

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
    notifyUser("Welcome to the tutorial for our Annotation Competition!\n Press enter to continue.");
    submitButton.disabled = true;
    skipButton.disabled = true;
    tagField.disabled = true;
    startButton.value = "Restart Tutorial"
    nextButton.hidden = false;
}

function explainPurpose() {
    notifyUser("The goal of this game is to crowdsource the tagging of images\n" +
        "To make it more exciting, we give you points!\n Press enter to continue");
}

function promptTag() {
    submitButton.disabled = false;
    tagField.disabled = false;
    notifyUser("Now you're ready to provide a tag.\n Please enter 'castle'");
}

function reactToTag() {
    submitButton.disabled = true;
    tagField.disabled = true;
    score.innerText = '3';
    notifyUser("Well done!\n You have now received points. \n The tag has been added to the list" +
        "\n Press enter to continue");
}

function updateTimer() {
    deadline--;
    timer.innerHTML = deadline + " s";
    timemeter.value = deadline;
    if (deadline <= 0) {
        submitButton.disabled = true;
        submitButton.value = "Time is up!";
        skipButton.value = "Restart";
        skipButton.disabled = false;
    }
}

function explainTimer() {
    setInterval(updateTimer, 1000);
    notifyUser("The game is on a timer\n" +
        "Wait until the time is up\n" +
        "Then press the \"Restart\" to get a new image");
}

function promptnewImage() {
    skipButton.disabled = false;
    notifyUser("You can request a new image by pressing Start Over");
}

function promptSkip() {
    deadline = 60;
    updateTimer();
    clearInterval(timer);
    skipButton.value = "Skip";
    skipButton.disabled = false;

    notifyUser("You can also skip an image by pressing Skip");
}

function displayDone() {
    notifyUser("Congratulations, you've completed the tutorial!\n" +
        "Press enter to start the game!");
}

function setImgToSkip() {
    img.src = "../static/img/tutorial_2.jpg";
}

function setLastImage() {
    img.src = "../static/img/tutorial_3.jpg";
}

function redirectToClassic() {
    window.location = tagForm.dataset.classicurl
}

function resetFocus() {
    snackbar.focus();
}

function advanceState() {
    tutorialState++;
    switch (tutorialState) {
        case tutorialState = 1:
            explainPurpose();
            break;
        case tutorialState = 2:
            nextButton.hidden = false;
            promptTag();
            break;
        case tutorialState = 3:
            resetFocus();
            reactToTag();
            break;
        case tutorialState = 4:
            explainTimer();
            break;
        case tutorialState = 5:
            nextButton.hidden = false;
            setImgToSkip();
            promptSkip();
            break;
        case tutorialState = 6:
            setLastImage();
            displayDone();
            break;
        case tutorialState = 7:
            nextButton.hidden = false;
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
    var evt = evt || window.event;
    if (tutorialState == 2 || tutorialState == 5 || tutorialState == 7) {
        return;
    }

    if (evt.keyCode == 13) {
        advanceState();
    }
};

function notifyUser(msg) {
    const snackbar = document.getElementById('snackbar');
    const data = {
        message: msg,
        timeout: 7500
    };
    snackbar.MaterialSnackbar.showSnackbar(data);
}
