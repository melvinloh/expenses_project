console.log("register.js success");

const usernameField = document.querySelector("#usernameField");
const usernameFeedback = document.querySelector('#validationServerUsernameFeedback');

usernameField.addEventListener("keyup", e => {
    //console.log(e.target.value);
    const usernameValue = e.target.value;

    if (usernameValue.length > 0) {

        // loading when throttle
        usernameFeedback.innerHTML =  `
        <div class="spinner-border spinner-border-sm text-warning" role="status">
            <span class="visually-hidden">Loading...</span>
        </div>
        <span class="text-warning">loading</span>
        `

        fetch("/authentication/validate-username", {
            method : 'POST',
            body: JSON.stringify({
                username: usernameValue
            })
        })
        .then(response => response.json())
        .then(result => {
            console.log(result);

            // invalid username
            if (result.username_error) {
                usernameField.classList.remove("is-valid");
                usernameField.classList.add("is-invalid");

                usernameFeedback.classList.remove("valid-feedback");
                usernameFeedback.classList.add("invalid-feedback");

                usernameFeedback.innerHTML = `<p> ${result.username_error} </p>`;
            }

            if (result.username_valid) {
                usernameField.classList.remove("is-invalid");
                usernameField.classList.add("is-valid"); 

                usernameFeedback.classList.remove("invalid-feedback");
                usernameFeedback.classList.add("valid-feedback");

                usernameFeedback.innerHTML = `<p> ${result.username_valid} </p>`;
            }

        })
    } else {
        usernameField.classList.remove("is-valid");
        usernameField.classList.remove("is-invalid");

        usernameFeedback.classList.remove("invalid-feedback");
        usernameFeedback.classList.remove("valid-feedback");

        usernameFeedback.innerHTML = null;
    }

})