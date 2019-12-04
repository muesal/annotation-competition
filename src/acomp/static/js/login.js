'use strict';

function writeToJson(username, userpassword) {
    var obj = {
        name: username,
        password: userpassword
    };
    return JSON.stringify(obj);
}

function handleLogin(e) {
    e.preventDefault();
    var name = document.getElementById("loginTxt2").value;
    var password = document.getElementById(loginpswd);
    var currentUrl = window.location.href;
    var requestUrl = currentUrl + "/data";
    var payload = writeToJson(name, );
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

var loginForm = document.getElementById("loginForm");
loginForm.addEventListener("submit", handleLogin);
loginForm.addEventListener("text", handleLogin);
loginForm.addEventListener("password", handleLogin);
var button = document.getElementById("loginSubmitButton");
button.addEventListener("click", handleLogin);

