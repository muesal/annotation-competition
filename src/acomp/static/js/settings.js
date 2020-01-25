'use strict';

const csrf_token = document.getElementById("csrf_token");
const loginname = document.getElementById("newloginname");
const paragraph = document.getElementById("feedbackParagraph");
const password = document.getElementById("newpswd");
const passwordConfirm = document.getElementById("newpswdConfirm");
const form = document.getElementById("NameForm");

loginname.addEventListener("input", checkLoginname);
password.addEventListener("input", checkPasswords);
passwordConfirm.addEventListener("input", checkPasswords);
