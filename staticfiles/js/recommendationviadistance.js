document.body.addEventListener("click", function (event) {
    if (event.target.classList.contains("order-now-btn")) {
        const dishId = event.target.getAttribute("data-dish-id");
        const dishName = event.target.getAttribute("data-dish-name");

        console.log(`🛒 Order Now clicked. Dish ID: ${dishId}, Dish Name: ${dishName}`);

        if (!dishId || dishId === "undefined" || dishId === "null") {
            console.error("❌ dishId is missing.");
            alert("Error: Dish ID is missing. Please try again.");
            return;
        }

        const modalElement = document.getElementById("orderModal");
        if (!modalElement) {
            console.error("❌ orderModal not found in the DOM.");
            return;
        }

        const orderModal = new bootstrap.Modal(modalElement);
        orderModal.show();

        setTimeout(() => {
            const restaurantList = document.getElementById("restaurantList");
            if (!restaurantList) {
                console.error("❌ #restaurantList not found.");
                return;
            }

            document.getElementById("selectedDish").textContent = dishName;
            restaurantList.innerHTML = `<li class='list-group-item'>🔍 Searching...</li>`;

            if (typeof window.getUserLocation === "function") {
                window.getUserLocation((userLocation) => {
                    if (userLocation) {
                        fetchNearbyRestaurants(dishId, dishName, userLocation);
                    } else {
                        restaurantList.innerHTML = `<li class='list-group-item text-danger'>❌ Unable to determine your location.</li>`;
                    }
                });
            } else {
                console.error("❌ getUserLocation function is not defined.");
                restaurantList.innerHTML = `<li class='list-group-item text-danger'>❌ Location function not available.</li>`;
            }
        }, 500);
    }
});

async function fetchNearbyRestaurants(dishId, dishName, userLocation) {
    if (!dishId) {
        console.error("❌ dishId is missing.");
        return;
    }

    try {
        const apiUrl = `/platform_db/get_nearby_restaurants?dish_id=${dishId}&lat=${userLocation.lat}&lon=${userLocation.lon}`;
        console.log(`🌍 Fetching restaurants: ${apiUrl}`);

        const response = await fetch(apiUrl);

        if (!response.ok) {
            throw new Error(`❌ Server returned status ${response.status}`);
        }

        const data = await response.json();
        console.log("✅ API Response:", data);

        if (data.error) {
            console.error("❌ API Error:", data.error);
            return;
        }

        let restaurantList = document.getElementById("restaurantList");
        if (!restaurantList) {
            console.warn("⚠️ #restaurantList not found immediately, waiting...");
            await new Promise(resolve => setTimeout(resolve, 500));
            restaurantList = document.getElementById("restaurantList");
        }

        if (!restaurantList) {
            console.error("❌ Still cannot find #restaurantList.");
            return;
        }

        restaurantList.innerHTML = "";

        if (!data.restaurants || data.restaurants.length === 0) {
            restaurantList.innerHTML = "<li class='list-group-item'>⚠️ No restaurants found for this dish.</li>";
            return;
        }

        data.restaurants.forEach(restaurant => {
            console.log(`✅ Found restaurant: ${restaurant.name}, ID: ${restaurant.rest_id || "MISSING"}`);

            if (!restaurant.rest_id) {
                console.error("❌ restaurant.rest_id is missing or undefined!");
                return;
            }

            const listItem = document.createElement("li");
            listItem.className = "list-group-item d-flex justify-content-between align-items-center";

            let content = `
                <div>
                    <span><strong>${restaurant.name}</strong> (${restaurant.distance} km away)</span>
            `;

            // ✅ Show Add to Cart only if logged in
            if (typeof isAuthenticated !== "undefined" && isAuthenticated) {
                content += `
                    <div class="input-group mt-2">
                        <input type="number" id="quantity-${restaurant.rest_id}" 
                               class="form-control form-control-sm quantity-input" 
                               value="1" min="1">
                        <button class="btn btn-primary btn-sm recommend-add-to-cart"
                                data-dish-id="${dishId}"  
                                data-dish-name="${dishName}"  
                                data-rest-id="${restaurant.rest_id}"  
                                data-rest-name="${restaurant.name}">
                            🛒 Add to Cart
                        </button>
                    </div>
                `;
            } else {
                content += `
                    <div class="mt-2 text-danger">
                        ⚠️ Login to add this item to your cart.
                    </div>
                `;
            }

            content += `</div>`;
            listItem.innerHTML = content;
            restaurantList.appendChild(listItem);
        });

    } catch (error) {
        console.error("❌ Error fetching restaurants:", error);
    }
}


// ✅ Event Delegation for Adding to Cart from Recommendations
document.body.addEventListener("click", function (event) {
    if (event.target.classList.contains("recommend-add-to-cart")) {
        const dishId = event.target.getAttribute("data-dish-id");
        const dishName = event.target.getAttribute("data-dish-name");
        const restaurantId = event.target.getAttribute("data-rest-id");
        const restaurantName = event.target.getAttribute("data-rest-name");
        const quantityInput = document.getElementById(`quantity-${restaurantId}`);
        const quantity = quantityInput ? parseInt(quantityInput.value) : 1;

        addToCartFromRecommendation(dishId, dishName, restaurantId, restaurantName, quantity);
    }
});

function getCSRFToken() {
    return document.cookie.split("; ")
        .find(row => row.startsWith("csrftoken="))
        ?.split("=")[1] || "";
}

function addToCartFromRecommendation(dishId, dishName, restaurantId, restaurantName, quantity) {
    quantity = parseInt(quantity);
    if (quantity < 1) {
        alert("⚠️ Please select at least 1 quantity.");
        return;
    }

    console.log("🛠️ Sending add-to-cart request from recommendation:", { dishId, restaurantId, restaurantName, quantity });

    fetch("/platform_db/cart/add/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken()
        },
        credentials: "same-origin",
        body: JSON.stringify({
            dishId: dishId,
            restaurantId: restaurantId,
            quantity: quantity
        })
    })
    .then(response => {
        if (!response.ok) {
            if (response.status >= 500) {
                throw new Error(`❌ Server error ${response.status}. Please try again later.`);
            } else if (response.status >= 400) {
                return response.json().then(data => { throw new Error(`⚠️ ${data.error || "Bad request"}`); });
            } else {
                throw new Error(`❌ Unexpected response ${response.status}`);
            }
        }
        return response.json();
    })
    .then(data => {
        console.log("✅ Item added successfully:", data.message);
        alert(`✅ ${quantity} x ${dishName} added to cart!`);
        loadCart();
    })
    .catch(error => {
        console.error("❌ AJAX error:", error.message);
        alert(error.message);
    });

   
}
