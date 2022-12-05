console.log("main.js success");

flashMessages = document.querySelector('#flashMessages');

document.addEventListener("DOMContentLoaded", clearFlashMessages());

// clearFlashMessages
function clearFlashMessages() {
    setTimeout(function() { flashMessages.innerHTML = null; }, 5000);
}