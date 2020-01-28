'use strict';

const csrf_token = document.getElementById("csrf_token");
const loginname = document.getElementById("loginname");
const password = document.getElementById("loginpswd");
const passwordConfirm = document.getElementById("loginpswdConfirm");
const form = document.getElementById("signupForm");
const snackbar = document.getElementById('snackbar');

loginname.addEventListener("input", checkLoginname);
password.addEventListener("input", checkPasswords);
passwordConfirm.addEventListener("input", checkPasswords);
