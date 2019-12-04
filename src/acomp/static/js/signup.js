'use strict';

const currentUrl = window.location.href;
const requestUrl = currentUrl + "/data";

function writeToJson(username, userpassword) {
    var obj = {
        name: username,
        password: userpassword
    };
    return JSON.stringify(obj);
}

async function handleSignup(e) {
    e.preventDefault();
    console.log("handling signup");

    var name = document.getElementById("loginTxt2").value;
    var password = document.getElementById("loginpswd").value;
    var passwordConfirm = document.getElementById("loginpswdConfirm").value;
    console.log(name + ":" + password + "," + passwordConfirm);
    if (password !== passwordConfirm) {
        var paragraph = document.getElementById("feedbackParagraph");
        paragraph.textContent += "Please make sure to confirm your password";
        return;

    }
    var payload = writeToJson(name, password);

    try {
        const response = await fetch(requestUrl, {
            method: 'POST',
            body: payload,
            headers: {
                'Content-Type': 'application/json'
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


var signupForm = document.getElementById("signupForm");
signupForm.addEventListener("submit", handleSignup);
signupForm.addEventListener("text", handleSignup);
signupForm.addEventListener("password", handleSignup);
var button = document.getElementById("loginSubmitButton");
button.addEventListener("click", handleSignup);

