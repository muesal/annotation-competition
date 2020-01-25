'use strict';

const csrf_token = document.getElementById("csrf_token");
const loginname = document.getElementById("loginname");
const paragraph = document.getElementById("feedbackParagraph");
const password = document.getElementById("loginpswd");
const passwordConfirm = document.getElementById("loginpswdConfirm");
const form = document.getElementById("signupForm");

loginname.addEventListener('input', checkLoginname);
password.addEventListener('input', checkPasswords);
passwordConfirm.addEventListener('input', checkPasswords);
