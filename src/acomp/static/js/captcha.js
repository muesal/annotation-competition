'use strict';

var deadline = 60;
var timer = setInterval(updateTimer, 1000);
var numImages = 0;

const currentUrl = window.location.href;
const requestUrl = currentUrl + "/data";
const csrf_token = document.getElementById("csrf_token");
const skipButton = document.getElementById("btnSkip");
getCaptchaData();


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
        for (var i = 0; i < images.length; i++) {
            const btn = document.createElement("BUTTON");
            const current = i.valueOf();
            const img = document.createElement('img');
            img.src = images[i];
            imagesInHtml.appendChild(img);
            btn.innerHTML = i.toString();
            btn.setAttribute("class", "mdl-button mdl-js-button mdl-button--raised mdl-button--colored captcha-button");
            btn.setAttribute("id", "select-" + current);
            btn.addEventListener("click", function () {
                    selectImage(current);
                }
            );
            imagesInHtml.appendChild(btn);
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
            document.getElementById("select-" + i).disabled = true;
        }
        skipButton.value = "Next";
    }
}


function handleSkip(e){
    e.preventDefault();
    getCaptchaData();
}

skipButton.addEventListener("click", handleSkip);