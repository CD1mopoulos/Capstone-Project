document.addEventListener("DOMContentLoaded", function () {
    const profileIcons = [
        document.getElementById("profile-icon"),
        document.getElementById("profile-icon-offcanvas")
    ];

    const cartIcons = [
        document.getElementById("cart-icon"),
        document.getElementById("cart-icon-offcanvas")
    ];

    const profileSection = document.getElementById('profileSection');
    const cartSection = document.getElementById('cartSection');

    function hideOffcanvasIfOpen() {
        const offcanvasElement = document.querySelector('.offcanvas.show');
        if (offcanvasElement) {
            const offcanvasInstance = bootstrap.Offcanvas.getInstance(offcanvasElement);
            if (offcanvasInstance) {
                offcanvasInstance.hide();
            }
        }
    }

    profileIcons.forEach(icon => {
        if (icon) {
            icon.addEventListener("click", function () {
                hideOffcanvasIfOpen();

                if (profileSection.style.display === 'block') {
                    profileSection.style.display = 'none';
                } else {
                    profileSection.style.display = 'block';
                    cartSection.style.display = 'none'; // hide cart if open
                    window.scrollTo({ top: profileSection.offsetTop - 80, behavior: 'smooth' });
                }
            });
        }
    });

    cartIcons.forEach(icon => {
        if (icon) {
            icon.addEventListener("click", function () {
                hideOffcanvasIfOpen();

                if (cartSection.style.display === 'block') {
                    cartSection.style.display = 'none';
                } else {
                    cartSection.style.display = 'block';
                    profileSection.style.display = 'none'; // hide profile if open
                    window.scrollTo({ top: cartSection.offsetTop - 80, behavior: 'smooth' });
                }
            });
        }
    });
});
