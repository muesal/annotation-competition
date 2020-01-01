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
            setImages(json.image);
            setTags(json.tags);
        } else {
            console.error('Error:', response.statusText); // TODO: notify user
        }
    } catch (err) {
        console.error('Error:', err);
    }
}


async function sendSelection(num) {
    var values = {
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
    console.log("Setting images");
    var imagesInHtml = document.getElementById("captchaImages");

    imagesInHtml.innerText = "";

    try {
        var i;
        for (i = 0; i < images.length; i++) {
            var img = document.createElement('img');
            img.src = images[i];
            imagesInHtml.appendChild(img);
            var btn = document.createElement("BUTTON");
            btn.innerHTML = i.toString();
            const current = i.valueOf();
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
    var tagsInHtml = document.getElementById("captchaTags");
    tagsInHtml.innerText = "";
    var i;
    var tagString = "";
    for (i = 0; i < newtags.length - 1; i++) {
        tagString += newtags[i] + ", "
    }
    tagString += newtags[newtags.length - 1];
    tagsInHtml.innerText = tagString;


}

