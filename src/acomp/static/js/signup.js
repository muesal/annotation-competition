'use strict';

const csrf_token = document.getElementById("csrf_token");
const loginname = document.getElementById("login/name");
const paragraph = document.getElementById("feedbackParagraph");
const password = document.getElementById("loginpswd");
const passwordConfirm = document.getElementById("loginpswdConfirm");
const form = document.getElementById("signupForm");

function writeToJson(username) {
    const obj = {
        name: username,
    };
    return JSON.stringify(obj);
}

async function checkLoginname(e) {
    loginname.setCustomValidity('');
    if (!loginname.checkValidity()) {
        loginname.setCustomValidity('Please use alphanumeric characters and not more than 512');
        return;
    }

    const payload = writeToJson(loginname.value);

    try {
        const response = await fetch(form.dataset.datauri, {
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
            if (json.available != '1') {
                loginname.setCustomValidity('This username is already taken, please choose another name.');
                return;
            }
        } else {
            console.error('Error:', response.statusText); // TODO: notify user
        }
    } catch (err) {
        console.error('Error:', err);
    }
}

async function checkPasswords(e) {
    passwordConfirm.setCustomValidity('');
    if (password.value !== passwordConfirm.value) {
        passwordConfirm.setCustomValidity('Please make sure to confirm your password');
        return;
    }

    // https://haveibeenpwned.com/API/v3#SearchingPwnedPasswordsByRange
    const apiurl = 'https://api.pwnedpasswords.com/range/';
    const hash = await digest(password.value);
    const fetchurl = apiurl + hash.substring(0, 5);
    var regex = new RegExp('^' + hash.slice(5) + ':(\\d+)', 'im');
    console.log('Search for:', regex.source);

    try {
        const response = await fetch(fetchurl);
        console.log('Sent:', fetchurl);
        if (response.ok) {
            const data = await response.text();
            console.log('Success:', data);
            if (regex.test(data)) {
                paragraph.textContent += "Your password might be insecure";
                return;
            } else {
                console.log('Not yet been pwned.');
            }
        } else {
            console.error('Error:', response.statusText); // TODO: notify user
        }
    } catch (err) {
        console.error('Error:', err);
    }
}

// https://developer.mozilla.org/en-US/docs/Web/API/SubtleCrypto/digest#Converting_a_digest_to_a_hex_string
async function digest(str) {
    const strUint8 = new TextEncoder().encode(str);
    const hashBuffer = await crypto.subtle.digest('SHA-1', strUint8);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
    console.log('SHA-1:', hashHex);
    return hashHex;
}

loginname.addEventListener('input', checkLoginname);
password.addEventListener('input', checkPasswords);
passwordConfirm.addEventListener('input', checkPasswords);
