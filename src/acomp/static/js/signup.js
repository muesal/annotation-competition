'use strict';


function writeToJson(username, userpassword) {
    var obj = {
        name: username,
        password: userpassword
    };
    return JSON.stringify(obj);
}

function handleSignup(e) {
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

    var currentUrl = window.location.href;
    var requestUrl = currentUrl + "/data";
    var payload = writeToJson(name, password);
    console.log(payload);

    fetch(requestUrl,
        {
            method: "POST",
            headers: {
                'Content-Type': 'application/json'
            },
            body: payload,
        })
        .then(function (res) {
            return res.json();
        })
        .then(function (data) {
            console.log(JSON.stringify(data))
        });
}

var signupForm = document.getElementById("signupForm");
signupForm.addEventListener("submit", handleSignup);
signupForm.addEventListener("text", handleSignup);
signupForm.addEventListener("password", handleSignup);
var button = document.getElementById("loginSubmitButton");
button.addEventListener("click", handleSignup);

