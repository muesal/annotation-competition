'use strict';

var deadline = 60;
var timer = setInterval(updateTimer, 1000);
var numImages = 0;

const currentUrl = window.location.href;
const requestUrl = currentUrl + "/data";
const csrf_token = document.getElementById("csrf_token");
const skipButton = document.getElementById("btnSkip");
getCaptchaData();

var listeners = [];


async function getCaptchaData() {
    console.log("Getting data");
    try {
        const response = await fetch(requestUrl);
        if (response.ok) {
            const json = await response.json();
            console.log('Success:', JSON.stringify(json));
            setImages(json.images);
            setTags(json.tags);
            setTimer(json.timelimit);
        } else {
            console.error('Error:', response.statusText); // TODO: notify user
        }
    } catch (err) {
        console.error('Error:', err);
    }
}

async function sendSelection(num) {
    const values = {
        'captcha': num
    };
    const payload = JSON.stringify(values);

    try {
        const response = await fetch(requestUrl, {
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
            hightlightImages(json.message, num);
        } else {
            console.error('Error:', response.statusText); // TODO: notify user
        }
    } catch (err) {
        console.error('Error:', err);
    }
}

function setImages(images) {
    const imagesInHtml = document.getElementById("captchaImages");
    console.log("Setting images");
    imagesInHtml.innerText = "";
    try {
        numImages = images.length;
        listeners = [];
        for (var i = 0; i < images.length; i++) {
            const current = i.valueOf();
            const img = document.createElement('img');
            img.className = "captchaimage";
            img.src = images[i];
            img.id = "select-" + current;
            imagesInHtml.appendChild(img);
            var selectFunction = function () {
                selectImage(current);
            };
            listeners.push(selectFunction);

            img.addEventListener("click", selectFunction
            );
        }
    } catch (e) {
        console.log(e)
    }
}

function selectImage(num) {
    console.log("Selected " + num);
    sendSelection(num);
}

function setTags(newtags) {
    const tagsInHtml = document.getElementById("captchaTags");
    var tagString = "";
    tagsInHtml.innerText = "";
    for (var i = 0; i < newtags.length - 1; i++) {
        tagString += newtags[i] + ", "
    }
    tagString += newtags[newtags.length - 1];
    tagsInHtml.innerText = tagString;
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

function updateTimer() {
    deadline--;
    document.getElementById("timer").innerHTML = deadline + " s";
    document.getElementById("timemeter").value = deadline;
    if (deadline <= 0) {
        clearInterval(timer);
        for (var i = 0; i < numImages; i++) {
            const currentimg = document.getElementById("select-" + i);
            currentimg.className = "captchaimageDisabled";
        }
        skipButton.value = "Start Over";
    }
}

function removeImages() {
    for (var i = 0; i < numImages; i++) {
        const currentimg = document.getElementById("select-" + i);
        currentimg.removeEventListener("click", listeners[i]);
        currentimg.removeAttribute("id");
    }
}

function handleSkip(e) {
    e.preventDefault();
    removeImages();
    getCaptchaData();
}

function highlightImageCorrect(num) {
    const element = document.getElementById("select-" + num);
    element.classList.add("captchaimageCorrect");
}

function hightlightImageIncorrect(num) {
    const element = document.getElementById("select-" + num);
    element.classList.add("captchaimageIncorrect");
}

function highlightChosen(num) {
    const element = document.getElementById("select-" + num);
    element.classList.add("captchaimageChosen");
}

function highlightNotChosen(num) {
    const element = document.getElementById("select-" + num);
    element.classList.add("captchaimageNotChosen");
}

function hightlightImages(correctImageNum, chosenImgNum) {
    var i;
    for (var i = 0; i < numImages; i++) {
        if (i == correctImageNum) {
            highlightImageCorrect(i)
        } else {
            hightlightImageIncorrect(i)
        }
        if (i == chosenImgNum) {
            highlightChosen(i)
        } else {
            highlightNotChosen(i)
        }
    }
}

skipButton.addEventListener("click", handleSkip);
