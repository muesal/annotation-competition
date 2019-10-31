var score = 0;
var deadline = 60;
const classicTimeLimit = 20;
resetTimer();
setInterval(resetTimer, 60000);
setInterval(displayTimer, 1000);
setInterval(updateTimer, 1000);
var mentionedTags = [];


function myFunction() {
    document.getElementById("demo").innerHTML = "Hello World";
}

function writeToMentionedTags(tag) {
    console.log("Write to tags called");
    var node = document.createElement("LI");                 // Create a <li> node
    var textnode = document.createTextNode(tag.toString());// Create a text node
    node.appendChild(textnode);                              // Append the text to <li>
    document.getElementById("mentionedTags").appendChild(node);     // Append <li> to <ul> with id="myList"
    mentionedTags.push(tag);
    console.log(mentionedTags);
}

function sendTag() {
//TODO
}

function updateScore(delta) {
    score += delta;
    document.getElementById("score").innerHTML = "score: " + score.toString();
}

function loadImage() { //TODO


}

function handleOutbound(out) {//TODO
    myJson = JSON.stringify(out);
    console.log(myJson);
}

function handleInput(tag) {

    console.log("handleInput called");


    if (!isInputPermissible(tag)) {
        console.log("Input" + tag + " not permissible");
        return;
    }
    writeToMentionedTags(tag);
    writeTagToJson(tag);


}

function displayTimer() {
    console.log("display timer called");
    remaining = deadline;
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
    if (hasAlreadyBeenMentioned()){
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
function resetTotal() {
    resetTags();
    resetTimer();


}

function resetTags() {
    console.log("Resetting tags");
    mentionedTags = [];
    root = document.getElementById("mentionedTags");
    while( root.firstChild ){
        root.removeChild( root.firstChild );
    }

}

function hasAlreadyBeenMentioned(tag) {
    console.log(mentionedTags.includes(tag));
    return mentionedTags.includes(tag);
}

function reset() {
    resetTimer();

}
