document.addEventListener("DOMContentLoaded", function () {
    console.log("OrderNowHandler.js loaded successfully.");

    document.querySelectorAll(".order-now-btn").forEach(button => {
        button.addEventListener("click", function () {
            const restId = this.getAttribute("data-restaurant-id"); // Ensure this exists
            const dishId = this.getAttribute("data-dish-id");
            const restName = this.getAttribute("data-restaurant-name");

            if (!restId) {
                console.error("Error: Restaurant ID is undefined");
                alert("Error: Could not find the restaurant. Please try again.");
                return;
            }

            console.log(`Redirecting to restaurant ID: ${restId}`);
            window.location.href = `/restaurant/${restId}`;
        });
    });
});
