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


async function handleLogin(e) {
    e.preventDefault();
    var name = document.getElementById("loginTxt2").value;
    var password = document.getElementById("loginpswd").value;

    var payload = writeToJson(name, password);
    console.log(payload);

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

var loginForm = document.getElementById("loginForm");
loginForm.addEventListener("submit", handleLogin);
loginForm.addEventListener("text", handleLogin);
loginForm.addEventListener("password", handleLogin);
var button = document.getElementById("loginSubmitButton");
button.addEventListener("click", handleLogin);

