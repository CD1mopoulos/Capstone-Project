// Show cart when user clicks the cart button
document.getElementById("toggleCart")?.addEventListener("click", function () {
    let cartSection = document.getElementById("cartSection");
    if (cartSection) {
        cartSection.style.display = cartSection.style.display === "none" ? "block" : "none";
        loadCart();  // ✅ Fetch cart from backend
    }
});

// ✅ Load cart dynamically from the backend
function loadCart() {
    fetch("/platform_db/cart/get/", {  
        method: "GET",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken()
        },
        credentials: "same-origin"
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Server error ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (!data || !Array.isArray(data.cart)) {
            console.warn("🚫 Invalid or empty cart response:", data);
            clearCartUI();  // ✅ Clear the cart visually for anonymous users
            return;
        }
        console.log("🛒 Cart loaded:", data);
        renderCart(data.cart);
    })
    .catch(error => {
        console.error("❌ Error loading cart:", error);
        alert("⚠️ Error loading cart. Please try again.");
        clearCartUI();  // ✅ Ensure UI is cleared if there's an error
    });
}

// ✅ Function to clear the cart UI when logged out
function clearCartUI() {
    console.log("🧹 Clearing cart UI for logged-out user...");
    const cartContainer = document.getElementById("cartContainer");
    const cartSummary = document.getElementById("cartSummary");

    if (cartContainer) cartContainer.innerHTML = "<p class='text-muted'>🛒 Your cart is empty.</p>";
    if (cartSummary) cartSummary.innerHTML = "Total: €0.00";
}

// ✅ Update cart UI dynamically from backend data
function renderCart(cart) {
    const cartContainer = document.getElementById("cartContainer");
    const cartSummary = document.getElementById("cartSummary");

    if (!cartContainer || !cartSummary) {
        console.error("❌ Cart UI elements missing.");
        return;
    }

    cartContainer.innerHTML = ""; // Clear existing cart items

    if (!cart || cart.length === 0) {
        cartContainer.innerHTML = "<p class='text-muted'>🛒 Your cart is empty.</p>";
        cartSummary.innerHTML = "Total: €0.00";
        return;
    }

    let totalCost = 0;

    cart.forEach(item => {
        totalCost += item.price * item.quantity;

        const cartItem = document.createElement("div");
        cartItem.className = "cart-item d-flex align-items-center mb-2";
        cartItem.innerHTML = `
            <img src="${item.photo ? item.photo : '/static/images/default-placeholder.jpg'}" 
                 alt="${item.dishName}" 
                 width="80" height="80" 
                 style="border-radius: 10px; margin-right: 10px;">
            <div class="flex-grow-1">
                <strong>${item.dishName}</strong> from <em>${item.restaurantName}</em><br>
                €${item.price.toFixed(2)} x 
                <input type="number" class="cart-quantity" value="${item.quantity}" min="1" 
                       data-dish-id="${item.dishId}" data-restaurant-id="${item.restaurantId}" 
                       style="width: 50px;">
            </div>
            <style>
            .remove-item {
                width: 36px;
                height: 36px;
                border-radius: 50%;
                padding: 0;
                color: #fff;
                display: flex;
                justify-content: center;
                align-items: center;
            }
            .remove-item i {
                font-size: 18px;
                line-height: 1;
                color: white;
            }
        </style>

        <!-- Functional Button with White X -->
        <button class="btn btn-danger btn-sm remove-item"
            data-dish-id="${item.dishId}"
            data-restaurant-id="${item.restaurantId}">
            <i class="bi bi-x-lg"></i>
        </button>
        `;

        cartContainer.appendChild(cartItem);
    });

    // ✅ Update total cost instantly
    updateTotalCost(cart);

    // ✅ Attach event listeners dynamically
    attachCartEventListeners();
}

// ✅ Function to update total cost
function updateTotalCost(cart) {
    let totalCost = cart.reduce((sum, item) => sum + item.price * item.quantity, 0);
    document.getElementById("cartSummary").innerHTML = `Total: €${totalCost.toFixed(2)}`;
}

// ✅ Attach event listeners for quantity change and remove buttons
function attachCartEventListeners() {
    document.querySelectorAll(".cart-quantity").forEach(input => {
        input.addEventListener("change", function () {
            const dishId = this.getAttribute("data-dish-id");
            const restaurantId = this.getAttribute("data-restaurant-id");
            const newQuantity = parseInt(this.value, 10);

            if (newQuantity < 1 || isNaN(newQuantity)) {
                alert("⚠️ Quantity must be at least 1.");
                this.value = 1;
                return;
            }

            updateCartQuantity(dishId, restaurantId, newQuantity);
        });
    });

    document.querySelectorAll(".remove-item").forEach(button => {
        button.addEventListener("click", function () {
            const dishId = this.getAttribute("data-dish-id");
            const restaurantId = this.getAttribute("data-restaurant-id");

            console.log("🔍 Removing:", { dishId, restaurantId });
            removeFromCart(dishId, restaurantId);
        });
    });
}

// ✅ Function to update cart quantity and refresh UI
function updateCartQuantity(dishId, restaurantId, newQuantity) {
    console.log("🛠️ Updating quantity:", { dishId, restaurantId, newQuantity });

    fetch("/platform_db/cart/update/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken()
        },
        credentials: "same-origin",
        body: JSON.stringify({
            dishId: parseInt(dishId, 10),
            restaurantId: parseInt(restaurantId, 10),
            quantity: parseInt(newQuantity, 10)  
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            console.error("❌ Error updating quantity:", data.error);
            alert(`⚠️ ${data.error}`);
        } else {
            console.log("✅ Quantity updated:", data.message);
            renderCart(data.cart);
        }
    })
    .catch(error => {
        console.error("❌ AJAX error:", error);
        alert("⚠️ Error updating quantity. Try again.");
    });
}

// ✅ Remove item from cart
function removeFromCart(dishId, restaurantId) {
    console.log("🛠️ Attempting to remove item from cart:", { dishId, restaurantId });

    fetch("/platform_db/cart/remove/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken()
        },
        credentials: "same-origin",
        body: JSON.stringify({ dishId: parseInt(dishId, 10), restaurantId: parseInt(restaurantId, 10) })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            console.error("❌ Error:", data.error);
            alert(`⚠️ ${data.error}`);
        } else {
            console.log(`✅ Successfully removed dish ${dishId} from cart.`);
            loadCart(); // ✅ Refresh cart
        }
    })
    .catch(error => {
        console.error("❌ AJAX error:", error);
        alert("⚠️ Error removing item. Try again.");
    });
}

// ✅ Get CSRF Token from cookies
function getCSRFToken() {
    return document.cookie.split("; ")
        .find(row => row.startsWith("csrftoken="))
        ?.split("=")[1];
}

// ✅ Ensure cart only loads when user is logged in
document.addEventListener("DOMContentLoaded", function () {
    const userStatus = document.getElementById("userStatus");

    if (userStatus && userStatus.dataset.loggedIn === "true") {
        console.log("✅ User is logged in, loading cart...");
        loadCart();
    } else {
        console.log("🚫 User is not logged in. Skipping cart load.");
        clearCartUI();  // ✅ Ensure the cart UI clears after logout
    }
});
