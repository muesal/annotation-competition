'use strict';

const currentUrl = window.location.href;
const requestUrl = currentUrl + "/data";
const csrf_token = document.getElementById("csrf_token");
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
        for (var i = 0; i < images.length; i++) {
            const btn = document.createElement("BUTTON");
            const current = i.valueOf();
            const img = document.createElement('img');
            img.src = images[i];
            imagesInHtml.appendChild(img);
            btn.innerHTML = i.toString();
            btn.setAttribute("class", "mdl-button mdl-js-button mdl-button--raised mdl-button--colored");
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
