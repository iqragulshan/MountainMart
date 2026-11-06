setTimeout(function() {

    const messages = document.querySelectorAll('.flash-message');

    messages.forEach(function(message) {

        message.style.transition = "opacity 0.5s ease";
        message.style.opacity = "0";

        setTimeout(function() {
            message.remove();
        }, 500);

    });

}, 3000);