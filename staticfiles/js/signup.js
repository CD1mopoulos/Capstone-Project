document.addEventListener("DOMContentLoaded", function() {
    let signupModal = document.getElementById("signupModal");

    signupModal.addEventListener("shown.bs.modal", function() {
        let signupForm = document.getElementById("signupForm");

        if (signupForm) {
            signupForm.addEventListener("submit", function(event) {
                event.preventDefault();
                let formData = new FormData(this);

                fetch(signupUrl, {
                    method: "POST",
                    body: formData,
                    headers: {
                        "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                    }
                })
                .then(response => response.json())
                .then(data => {
                    let messageBox = document.getElementById("signupMessage");
                    messageBox.innerHTML = "";  // Clear previous messages

                    if (data.success) {
                        messageBox.innerHTML = "<p class='text-success'>Signup successful! Redirecting...</p>";
                        setTimeout(() => {
                            // Close the modal
                            let modal = bootstrap.Modal.getInstance(signupModal);
                            modal.hide();
                            
                            // Scroll to the home section after signup
                            window.location.hash = "#home";
                            location.reload(); // Refresh the content
                        }, 1500);
                    } else {
                        let errors = JSON.parse(data.error);
                        let errorMessages = "";
                        
                        if (errors.password2) {
                            errors.password2.forEach(error => {
                                errorMessages += `<p class='text-danger'>⚠️ ${error.message}</p>`;
                            });
                        }
                        
                        messageBox.innerHTML = errorMessages;
                    }
                })
                .catch(error => console.log("Signup Error:", error));
            });
        }
    });
});
