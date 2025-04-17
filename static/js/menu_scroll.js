document.addEventListener("DOMContentLoaded", function () {
    console.log("✅ JavaScript loaded successfully.");

    if (typeof getCart === "undefined") {
        console.warn("⚠️ getCart() is not defined. Loading cart from the backend instead.");
        loadCart();
    } else {
        try {
            getCart();
        } catch (error) {
            console.error("❌ Error retrieving cart:", error);
        }
    }

    document.querySelectorAll(".order-now").forEach(button => {
        button.addEventListener("click", function () {
            const restId = this.getAttribute("data-rest-id");
            const restName = this.getAttribute("data-rest-name");
            console.log(`📌 Fetching menu for restaurant ID: ${restId}`);

            const menuList = document.getElementById("menuList");
            const restaurantName = document.getElementById("restaurantName");
            const menuModalElement = document.getElementById("menuModal");

            if (!menuList || !restaurantName || !menuModalElement) {
                console.error("❌ Missing menu elements in the DOM.");
                return;
            }

            restaurantName.innerText = `Menu for ${restName}`;
            menuList.innerHTML = "";

            fetch(`/platform_db/get-menu/${restId}/`, {
                headers: { "X-Requested-With": "XMLHttpRequest" }
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`❌ Server error ${response.status}: ${response.statusText}`);
                    }
                    return response.json();
                })
                .then(data => {
                    console.log("✅ Received menu data:", data);

                    if (!data || !Array.isArray(data.menu_items)) {
                        throw new Error("❌ Invalid response format: Missing `menu_items` array");
                    }

                    if (data.menu_items.length === 0) {
                        menuList.innerHTML = "<li class='list-group-item'>⚠️ No dishes available.</li>";
                    } else {
                        data.menu_items.forEach(item => {
                            console.log("🛠️ Checking item data:", item);

                            if (!item.dish_id) {
                                console.error("❌ Missing dishId in API response!", item);
                            }

                            let itemPrice = Number(item.price);
                            if (isNaN(itemPrice)) {
                                console.error("❌ Invalid price for item:", item);
                                itemPrice = 0.00;
                            }

                            const listItem = document.createElement("li");
                            listItem.className = "list-group-item";

                            let content = `
                                <div class="row w-100">
                                    <div class="col-12 col-md-9 mb-2">
                                        <strong>${item.dish_name}</strong> - €${itemPrice.toFixed(2)}
                                        <br><em>${item.description}</em>
                                        <br>Ingredients: ${item.ingredients}
                                        ${item.photo ? `<br><img src="${item.photo}" width="100" alt="${item.dish_name}" style="border-radius: 8px;">` : ""}
                                    </div>
                            `;

                            if (typeof isAuthenticated !== "undefined" && isAuthenticated) {
                                content += `
                                    <div class="col-12 col-md-3 d-flex justify-content-md-end justify-content-start flex-md-nowrap flex-wrap align-items-center gap-2 mt-md-0 mt-2">
                                        <input type="number" min="1" value="1" class="form-control form-control-sm quantity" style="max-width: 60px; text-align: center;" data-dish-id="${item.dish_id}">
                                        <button class="btn btn-sm btn-primary add-to-cart"
                                            data-dish-id="${item.dish_id}"  
                                            data-dish-name="${item.dish_name}" 
                                            data-price="${itemPrice.toFixed(2)}" 
                                            data-rest-id="${restId}"  
                                            data-rest-name="${restName}"
                                            data-photo="${item.photo ? item.photo : '/static/images/default-placeholder.jpg'}">
                                            🛒 Add to Cart
                                        </button>
                                    </div>
                                `;
                            } else {
                                content += `
                                    <div class="col-12 mt-2">
                                        <span class="text-danger">⚠️ Login to add items to cart</span>
                                    </div>
                                `;
                            }

                            content += `</div>`; // close row

                            listItem.innerHTML = content;
                            menuList.appendChild(listItem);
                        });
                    }

                    const menuModal = new bootstrap.Modal(menuModalElement);
                    menuModal.show();
                })
                .catch(error => {
                    console.error("❌ Error loading menu:", error);
                    alert("⚠️ Error loading menu. Please try again.");
                });
        });
    });

    document.body.addEventListener("click", function (event) {
        if (event.target.classList.contains("add-to-cart")) {
            addToCart(event.target);
        }
    });

    function addToCart(button) {
        if (typeof isAuthenticated === "undefined" || !isAuthenticated) {
            alert("⚠️ You must be logged in to add items to the cart.");
            return;
        }

        const dishId = button.getAttribute("data-dish-id");
        const dishName = button.getAttribute("data-dish-name");
        const restId = button.getAttribute("data-rest-id");
        const quantityInput = document.querySelector(`.quantity[data-dish-id="${dishId}"]`);
        const quantity = quantityInput ? parseInt(quantityInput.value) : 1;

        if (!dishId || !restId || isNaN(quantity) || quantity < 1) {
            alert("⚠️ Invalid item data. Please try again.");
            console.error("❌ Invalid add-to-cart data:", { dishId, restId, quantity });
            return;
        }

        const requestBody = {
            dishId: dishId,
            restaurantId: restId,
            quantity: quantity
        };

        console.log("🛠️ Sending add-to-cart request:", requestBody);

        fetch("/platform_db/cart/add/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken() || ""
            },
            credentials: "same-origin",
            body: JSON.stringify(requestBody)
        })
            .then(response => response.json().catch(() => {
                throw new Error(`❌ Response is not JSON (Status: ${response.status})`);
            }))
            .then(data => {
                if (data.error) {
                    console.error("❌ Error:", data.error);
                    alert(`⚠️ ${data.error}`);
                } else {
                    console.log("✅ Item added:", data.message);
                    alert(`✅ ${quantity} x ${dishName} added to cart!`);
                    loadCart();
                }
            })
            .catch(error => {
                console.error("❌ AJAX error:", error);
                alert("⚠️ Error adding item.");
            });
    }

    function loadCart() {
        console.log("🛒 Loading cart...");

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
                    throw new Error(`❌ Server error ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (!data || !Array.isArray(data.cart)) {
                    throw new Error("❌ Invalid cart response format");
                }

                console.log("✅ Cart loaded:", data.cart);
                renderCart(data.cart);
            })
            .catch(error => {
                console.error("❌ Error loading cart:", error);
            });
    }

    const viewCartButton = document.getElementById("viewCart");
    const cartSection = document.getElementById("cartSection");

    if (viewCartButton && cartSection) {
        viewCartButton.addEventListener("click", function () {
            const menuModal = bootstrap.Modal.getInstance(document.getElementById("menuModal"));
            if (menuModal) {
                menuModal.hide();
            }

            cartSection.style.display = "block";
            cartSection.scrollIntoView({ behavior: "smooth" });

            console.log("🛒 Scrolled to cart section");
        });
    } else {
        console.warn("⚠️ View Cart button or cart section not found in DOM.");
    }

    loadCart();
});
