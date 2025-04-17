document.addEventListener("DOMContentLoaded", () => {
    const profileBtn = document.getElementById("toggleProfile");
    const profileSection = document.getElementById("profileSection");

    if (profileBtn && profileSection) {
        profileBtn.addEventListener("click", () => {
            const isVisible = profileSection.style.display === "block";
            profileSection.style.display = isVisible ? "none" : "block";
            if (!isVisible) {
                profileSection.scrollIntoView({ behavior: "smooth" });
            }
        });
    }
});
