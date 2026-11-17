document.addEventListener("DOMContentLoaded", () => {

    const messages = document.querySelectorAll(".auto-hide-message");

    messages.forEach((message) => {

        setTimeout(() => {
            message.style.transition = "opacity 0.3s ease";
            message.style.opacity = "0";

            setTimeout(() => {
                message.remove();
            }, 300);

        }, 1500);

    });

});