document.addEventListener("DOMContentLoaded", function() {

    const scrollKey = "mountainMartScrollPosition";

    // Restore previous scroll position
    const savedPosition = sessionStorage.getItem(scrollKey);

    if (savedPosition !== null) {
        window.scrollTo(0, Number(savedPosition));
        sessionStorage.removeItem(scrollKey);
    }

    // Save scroll position before Add to Cart
    document.querySelectorAll(
        'form[action*="add_to_cart"]'
    ).forEach(function(form) {

        form.addEventListener("submit", function() {
            sessionStorage.setItem(scrollKey, window.scrollY);
        });

    });

});
document.addEventListener("DOMContentLoaded", function() {
    const scrollKey = "customerScrollPosition";

    // Restore previous scroll position
    const savedPosition = sessionStorage.getItem(scrollKey);

    if (savedPosition !== null) {
        window.addEventListener("load", function() {
            requestAnimationFrame(function() {
                requestAnimationFrame(function() {
                    window.scrollTo(0, Number(savedPosition));
                    sessionStorage.removeItem(scrollKey);
                });
            });
        });
    }

    // Save position before Add to Cart
    document.querySelectorAll(
        'form[action*="/customer/cart/add/"]'
    ).forEach(function(form) {
        form.addEventListener("submit", function() {
            sessionStorage.setItem(scrollKey, window.scrollY);
        });
    });
});

// Customer flash messages
document.addEventListener("DOMContentLoaded", function() {
    const messages = document.querySelectorAll(".auth-message");

    messages.forEach(function(message) {
        setTimeout(function() {
            message.style.transition = "opacity 0.5s ease";
            message.style.opacity = "0";

            setTimeout(function() {
                message.remove();
            }, 500);
        }, 1500);
    });
});