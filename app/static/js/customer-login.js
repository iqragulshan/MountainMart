const emailInput = document.getElementById("customer-email");

const savedEmails = JSON.parse(
    localStorage.getItem("customerEmails") || "[]"
);

const suggestionBox = document.createElement("div");
suggestionBox.className = "email-suggestions";

emailInput.parentNode.insertBefore(
    suggestionBox,
    emailInput.nextSibling
);

function showSuggestions() {
    suggestionBox.innerHTML = "";

    savedEmails.forEach(email => {
        const item = document.createElement("div");
        item.textContent = email;
        item.className = "email-suggestion";

        item.addEventListener("click", function() {
            emailInput.value = email;
            suggestionBox.style.display = "none";
        });

        suggestionBox.appendChild(item);
    });

    suggestionBox.style.display =
        savedEmails.length ? "block" : "none";
}

emailInput.addEventListener("focus", showSuggestions);

document.addEventListener("click", function(event) {
    if (
        event.target !== emailInput &&
        !suggestionBox.contains(event.target)
    ) {
        suggestionBox.style.display = "none";
    }
});

emailInput.form.addEventListener("submit", function() {
    const email = emailInput.value.trim();

    if (email && !savedEmails.includes(email)) {
        savedEmails.push(email);

        localStorage.setItem(
            "customerEmails",
            JSON.stringify(savedEmails)
        );
    }
});