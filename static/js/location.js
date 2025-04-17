// location.js

document.addEventListener("DOMContentLoaded", function () {
    console.log("✅ location.js is now loaded");

    /** Global function to get user location and fetch address */
    window.getUserLocation = async function (callback) {
        console.log("📍 Detecting location...");

        if (!navigator.geolocation) {
            console.warn("❌ Geolocation is not supported by this browser.");
            updateNavbarLocation("Geolocation not supported");
            return;
        }

        navigator.geolocation.getCurrentPosition(
            function (position) {
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;

                console.log(`📌 Location obtained: ${lat}, ${lon}`);

                // Call function to fetch full address
                getFullAddress(lat, lon, callback);
            },
            function (error) {
                console.error("⚠️ Geolocation error:", error);
                updateNavbarLocation("Unable to detect location");
            },
            { timeout: 10000, enableHighAccuracy: true, maximumAge: 0 }
        );
    };

    /** Fetches full address from coordinates */
    async function getFullAddress(lat, lon, callback) {
        try {
            console.log("🌍 Fetching full address from coordinates:", lat, lon);

            const response = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}`);
            if (!response.ok) throw new Error("❌ Failed to fetch location data");

            const data = await response.json();
            console.log("📌 Raw API Response:", data); // Debugging API response

            if (data && data.address) {
                // ✅ Handle all possible city variations
                const houseNumber = data.address.house_number ? `${data.address.house_number} ` : "";
                const street = data.address.road || data.address.neighbourhood || data.address.suburb || "Unknown Street";

                // ✅ Get the best available city-like value
                const city = data.address.city || data.address.town || data.address.village ||
                    data.address.municipality || data.address.county || "Unknown City";

                const country = data.address.country || "Unknown Country";

                // ✅ Final formatted address
                const formattedAddress = `${houseNumber}${street}, ${city}, ${country}`;
                console.log("📌 Clean Address:", formattedAddress);

                // Update UI
                updateNavbarLocation(formattedAddress);

                // Pass the data to the callback function if needed
                if (callback) callback({ lat, lon, formattedAddress });
            } else {
                console.warn("⚠️ No address found for coordinates.");
                updateNavbarLocation("⚠️ Address not available");
            }
        } catch (error) {
            console.error("❌ Error fetching location:", error);
            updateNavbarLocation("⚠️ Unable to fetch address");
        }
    }

    /** Updates navbar location text */
    function updateNavbarLocation(message) {
        const navbarLocation = document.getElementById("navbarLocation");
        if (navbarLocation) {
            navbarLocation.innerHTML = `📍 ${message}`;
        } else {
            console.error("❌ Navbar location element not found.");
        }
    }

    /** Function to fetch IP-based location as a fallback */
    async function fetchIPLocation(callback) {
        try {
            console.log("🌍 Fetching location using IP...");
            const response = await fetch("https://ipwho.is/?output=json");
            const data = await response.json();

            if (data.success && data.city && data.country) {
                console.log("✅ IP-based location found:", data.city, data.country);
                updateNavbarLocation(`${data.city}, ${data.country}`);
                callback({ city: data.city, country: data.country });
            } else {
                console.warn("⚠️ Failed to fetch IP-based location.");
                updateNavbarLocation("Location not available");
                callback(null);
            }
        } catch (error) {
            console.error("❌ Error fetching IP location:", error);
            updateNavbarLocation("Location not available");
            callback(null);
        }
    }

    /** Force location update on page load */
    getUserLocation(() => { });
});