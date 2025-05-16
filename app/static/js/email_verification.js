document.addEventListener("DOMContentLoaded", function () {
    const email1 = document.getElementById("email1");
    const email2 = document.getElementById("email2");
    const form = document.getElementById("form");
    const invalidEmail = document.getElementById("invalidEmail");
    const emailNotMatching = document.getElementById("EmailNotMatching");
    const invalidSubmission = document.getElementById("invalidSubmission");

    function isValidEmail(email) {
        const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        return emailRegex.test(email)
    }

    let email1Touched = false;
    let email2Touched = false;

    // Email Validation
    email1.addEventListener("blur", function() {
        email1Touched = true;
        if (!isValidEmail(email1.value)) {
            invalidEmail.style.display = "block";
        }
    });
    email1.addEventListener("input", function() {
        if (email1Touched) {
            if (!isValidEmail(email1.value)) {
                invalidEmail.style.display = "block";
            } else {
                invalidEmail.style.display = "none";
            }
        }
    });

    // Email Match Validation
    email2.addEventListener("blur", function() {
        console.log('hi')
        email2Touched = true;
        if (email1.value !== email2.value) {
            emailNotMatching.style.display = "block";
        }
    });
    email2.addEventListener("input", function() {
        if (email2Touched) {
            if (email1.value !== email2.value) {
                emailNotMatching.style.display = "block";
            } else {
                emailNotMatching.style.display = "none";
            }
        }
    });

    // Form submission checks
    form.addEventListener("submit", function (event) {
        invalidEmail.style.display = "none";
        emailNotMatching.style.display = "none";
        invalidSubmission.style.display = "none";

        const isEmailValid = isValidEmail(email1.value);
        const emailsMatch = email1.value === email2.value;
        let validSubmission = true;

        if (!isEmailValid) {
            invalidEmail.style.display = "block";
            validSubmission = false;
        }

        if (!emailsMatch) {
            emailNotMatching.style.display = "block";
            validSubmission = false;
        }

        if (!validSubmission) {
            invalidSubmission.style.display = "block";
            event.preventDefault();
        }
    });
});