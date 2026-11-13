document.addEventListener("DOMContentLoaded", function() {

    const scrollKey = "mountainMartScrollPosition";

    // Restore scroll position after cart update
    const savedPosition = sessionStorage.getItem(scrollKey);

    if (savedPosition !== null) {
        window.addEventListener("load", function() {
            requestAnimationFrame(function() {
                window.scrollTo(0, Number(savedPosition));
                sessionStorage.removeItem(scrollKey);
            });
        });
    }

    // Save scroll position before cart form submission
    document.querySelectorAll(
        ".quantity-form, .remove-form"
    ).forEach(function(form) {

        form.addEventListener("submit", function() {
            sessionStorage.setItem(scrollKey, window.scrollY);
        });

    });

    // Increase and decrease quantity
    document.querySelectorAll(".quantity-step").forEach(function(button) {

        button.addEventListener("click", function() {

            const form = this.closest(".quantity-form");
            const input = form.querySelector('input[name="quantity"]');

            const min = Number(input.min) || 1;
            const max = Number(input.max) || 999;

            let quantity = Number(input.value) || min;

            if (this.dataset.action === "increase") {
                quantity = Math.min(quantity + 1, max);
            } else if (this.dataset.action === "decrease") {
                quantity = Math.max(quantity - 1, min);
            }

            input.value = quantity;
            form.requestSubmit();

        });

    });

    // Update quantity when manually changed
    document.querySelectorAll(
        ".quantity-form input[name='quantity']"
    ).forEach(function(input) {

        input.addEventListener("change", function() {

            const min = Number(this.min) || 1;
            const max = Number(this.max) || 999;

            let quantity = Number(this.value) || min;

            quantity = Math.max(min, Math.min(quantity, max));
            this.value = quantity;

            this.form.requestSubmit();

        });

    });

});