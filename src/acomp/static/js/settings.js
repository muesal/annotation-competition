'use strict';

// TODO: use absolute immutable url
const currentUrl = window.location.href;
const requestUrl = currentUrl + "/data";

const loginname = document.getElementById("newloginname");
const paragraph = document.getElementById("feedbackParagraph");
const password = document.getElementById("newpswd");
const passwordConfirm = document.getElementById("newpswdConfirm");
const showChangeNameButton = document.getElementById("btnShowChangeName");
const showDeleteButton = document.getElementById("btnShowDeleteAccount");
const showPasswordButton = document.getElementById("btnShowChangePassword");
loginname.addEventListener("input", checkLoginname);
password.addEventListener("input", checkPasswords);
passwordConfirm.addEventListener("input", checkPasswords);
