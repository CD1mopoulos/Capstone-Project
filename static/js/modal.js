document.addEventListener("DOMContentLoaded", () => {
  // Apply modal logic only on Desktop & Tablets
  if (window.matchMedia("(min-width: 577px)").matches) {

    const loginForm = document.querySelector("#loginModal form");
    const signUpForm = document.querySelector("#signupModal form");

    const loginFields = document.querySelectorAll("#loginUsername, #loginPassword");
    const signUpFields = document.querySelectorAll(
      "#signupName, #signupSureName, #signupUsername, #signupEmail, #signupPassword, #signupConfirmPassword, #termsConditions"
    );

    const googleButtons = document.querySelectorAll(".btn-google");

    const disableRequiredFields = (fields) => {
      fields.forEach((field) => field.removeAttribute("required"));
    };

    const enableRequiredFields = (fields) => {
      fields.forEach((field) => field.setAttribute("required", "true"));
    };

    googleButtons.forEach((button) => {
      button.addEventListener("click", (event) => {
        event.preventDefault();
        if (button.closest("#loginModal")) {
          disableRequiredFields(loginFields);
          loginForm.submit();
        } else if (button.closest("#signupModal")) {
          disableRequiredFields(signUpFields);
          signUpForm.submit();
        }
      });
    });

    document.querySelectorAll("#loginModal .btn[type='submit'], #signupModal .btn[type='submit']").forEach((button) => {
      button.addEventListener("click", () => {
        if (button.closest("#loginModal")) {
          enableRequiredFields(loginFields);
        } else if (button.closest("#signupModal")) {
          enableRequiredFields(signUpFields);
        }
      });
    });

    const restoreRequiredOnModalClose = (modal, fields) => {
      modal.addEventListener("hidden.bs.modal", () => {
        enableRequiredFields(fields);
      });
    };

    const loginModal = document.querySelector("#loginModal");
    const signupModal = document.querySelector("#signupModal");

    if (loginModal) restoreRequiredOnModalClose(loginModal, loginFields);
    if (signupModal) restoreRequiredOnModalClose(signupModal, signUpFields);

    if (signupModal) {
      signupModal.addEventListener("hidden.bs.modal", function () {
        const form = signupModal.querySelector("form");
        form.reset();
        document.getElementById("eyeIconSignup").setAttribute("name", "eye-off-outline");
        document.getElementById("eyeIconSignupConfirm").setAttribute("name", "eye-off-outline");
      });
    }

    if (loginModal) {
      loginModal.addEventListener("hidden.bs.modal", function () {
        const form = loginModal.querySelector("form");
        form.reset();
        document.getElementById("eyeIconLogin").setAttribute("name", "eye-off-outline");
      });
    }
  }
});
