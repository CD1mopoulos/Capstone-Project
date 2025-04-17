window.onload = function () {
    let homeUrl = document.body.getAttribute("data-home-url") || "/"; // Fallback to "/"
    const navLinks = document.querySelectorAll(".nav-link");
    const sections = document.querySelectorAll("section");
    const offsetThreshold = 120; // Adjust threshold

    // Function to handle active class on navbar links
    function setActiveNav() {
        navLinks.forEach(link => link.classList.remove("active"));

        const currentPath = window.location.pathname;

        // Keep "About Us" and "Contact Us" active when on respective pages
        if (currentPath.includes("/about/")) {
            document.querySelector('a[href$="/about/"]')?.classList.add("active");
            return;
        }
        if (currentPath.includes("/contact/")) {
            document.querySelector('a[href$="/contact/"]')?.classList.add("active");
            return;
        }

        // Get current hash
        const currentHash = window.location.hash;

        if (!currentHash) {
            document.querySelector(`a[href="${homeUrl}#hero"]`)?.classList.add("active");
        } else {
            navLinks.forEach(link => {
                if (link.getAttribute("href") === `${homeUrl}${currentHash}`) {
                    link.classList.add("active");
                }
            });
        }
    }

    // Function to smoothly scroll to a section when clicking navbar links
    function handleNavigation(event) {
        let href = this.getAttribute("href");

        // Allow normal navigation for external links (e.g., "/about/", "/contact/")
        if (!href.startsWith("#")) {
            return;
        }

        event.preventDefault();
        let targetId = href.split("#")[1];

        if (targetId) {
            let targetSection = document.getElementById(targetId);
            if (targetSection) {
                window.history.pushState(null, "", homeUrl + `#${targetId}`);
                targetSection.scrollIntoView({ behavior: "smooth", block: "start" });

                setTimeout(setActiveNav, 300);
            }
        }
    }

    // Function to update navbar active state based on scroll position
    function handleScroll() {
        if (window.location.pathname !== homeUrl) return;

        let foundActive = false;

        sections.forEach(section => {
            const sectionTop = section.offsetTop - offsetThreshold;
            const sectionBottom = sectionTop + section.offsetHeight;
            const sectionId = section.getAttribute("id");
            const correspondingLink = document.querySelector(`a[href="${homeUrl}#${sectionId}"]`);

            if (window.scrollY >= sectionTop && window.scrollY < sectionBottom) {
                correspondingLink?.classList.add("active");
                foundActive = true;
            } else {
                correspondingLink?.classList.remove("active");
            }
        });

        if (!foundActive) {
            document.querySelector(`a[href="${homeUrl}#hero"]`)?.classList.add("active");
        }
    }

    // Ensure menu and home sections activate immediately when clicked
    navLinks.forEach(link => {
        link.addEventListener("click", handleNavigation);
    });

    // Handle hash navigation after redirection
    if (window.location.hash) {
        setTimeout(() => {
            let target = document.querySelector(window.location.hash);
            if (target) {
                target.scrollIntoView({ behavior: "smooth", block: "start" });
                setTimeout(setActiveNav, 300);
            }
        }, 500);
    }

    // Run functions on page load
    setActiveNav();
    handleScroll();

    // Listen for scroll events to update active navbar links dynamically
    window.addEventListener("scroll", handleScroll);
};
