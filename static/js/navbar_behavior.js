document.addEventListener("DOMContentLoaded", function () {
    const sectionLinks = document.querySelectorAll(".section-link");
    const homeLink = document.getElementById("homeLink");
    const homeUrl = document.body.getAttribute("data-home-url") || "/"; // Fallback to "/"
    const currentPath = window.location.pathname;

    // ✅ Prevent empty search submission
    const searchForms = document.querySelectorAll(".search-bar");
    searchForms.forEach(form => {
        form.addEventListener("submit", function (e) {
            const input = this.querySelector("input[name='q']");
            if (!input.value.trim()) {
                e.preventDefault();
                alert("Please type something to search for!");
            }
        });
    });

    // Function to smoothly scroll to a section
    function smoothScroll(targetId) {
        const targetSection = document.querySelector(targetId);
        if (targetSection) {
            targetSection.scrollIntoView({ behavior: "smooth", block: "start" });
        }
    }

    // Function to adjust links for About & Contact pages
    function adjustLinks() {
        sectionLinks.forEach(link => {
            let href = link.getAttribute("href");

            if (currentPath === "/about/" || currentPath === "/contact/") {
                if (href && href.startsWith("#")) {
                    link.setAttribute("href", homeUrl + href);
                }
            }
        });

        if (homeLink) {
            if (currentPath === "/about/" || currentPath === "/contact/") {
                homeLink.setAttribute("href", homeUrl || "/");
            } else {
                homeLink.setAttribute("href", "#hero");
            }
        }
    }

    // Function to set active navbar link based on scroll position
    function updateActiveLink() {
        if (currentPath !== "/") return;

        const sections = document.querySelectorAll("section");
        let foundActive = false;

        sections.forEach(section => {
            const sectionTop = section.offsetTop - 50;
            const sectionBottom = sectionTop + section.offsetHeight;
            const sectionId = section.getAttribute("id");
            const correspondingLink = document.querySelector(`a[href="#${sectionId}"]`);

            if (window.scrollY >= sectionTop && window.scrollY < sectionBottom) {
                correspondingLink?.classList.add("active");
                foundActive = true;
            } else {
                correspondingLink?.classList.remove("active");
            }
        });

        if (!foundActive) {
            document.querySelector(`a[href="#hero"]`)?.classList.add("active");
        }
    }

    // Handle click events for smooth scrolling
    sectionLinks.forEach(link => {
        link.addEventListener("click", function (event) {
            let href = this.getAttribute("href");

            if (href.startsWith("#")) {
                event.preventDefault();

                if (currentPath !== "/") {
                    window.location.href = homeUrl + href;
                } else {
                    smoothScroll(href);
                }
            }
        });
    });

    // Handle hash navigation after redirection
    if (window.location.hash) {
        setTimeout(() => {
            smoothScroll(window.location.hash);
        }, 500);
    }

    // Run functions on page load
    adjustLinks();
    updateActiveLink();

    window.addEventListener("scroll", updateActiveLink);
});
