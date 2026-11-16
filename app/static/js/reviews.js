document.addEventListener("DOMContentLoaded", function() {

    const ratingInput = document.getElementById("reviewRating");
    const starsContainer = document.getElementById("customerRatingStars");
    const ratingLabel = document.getElementById("customerRatingLabel");
    const reviewForm = document.getElementById("customerReviewForm");

    if (!ratingInput || !starsContainer || !ratingLabel) return;

    const stars = starsContainer.querySelectorAll(".rating-star");

    let selectedRating = 0;

    const ratingTexts = {
        0.5: "Very Poor",
        1: "Poor",
        1.5: "Below Average",
        2: "Fair",
        2.5: "Average",
        3: "Good",
        3.5: "Very Good",
        4: "Very Good",
        4.5: "Excellent",
        5: "Excellent"
    };

    stars.forEach(function(star) {

        // Display only ONE star in each button
        star.textContent = "★";

        function getRating(event) {
            const rect = star.getBoundingClientRect();
            const position = event.clientX - rect.left;
            const isLeftHalf = position < rect.width / 2;

            return Number(star.dataset.star) - (isLeftHalf ? 0.5 : 0);
        }

        star.addEventListener("pointermove", function(event) {
            showRating(getRating(event));
        });

        star.addEventListener("click", function(event) {
            selectedRating = getRating(event);

            ratingInput.value = selectedRating;

            showRating(selectedRating);
        });

    });

    function showRating(rating) {

        stars.forEach(function(star) {

            const starNumber = Number(star.dataset.star);
            let fill = 0;

            if (rating >= starNumber) {
                fill = 100;
            } else if (rating >= starNumber - 0.5) {
                fill = 50;
            }

            star.style.setProperty("--fill", fill + "%");
        });

        if (rating > 0) {
            ratingLabel.textContent =
                rating + " / 5 - " + ratingTexts[rating];
        } else {
            ratingLabel.textContent = "Select your rating";
        }
    }

    starsContainer.addEventListener("pointerleave", function() {
        showRating(selectedRating);
    });

    if (reviewForm) {
        reviewForm.addEventListener("submit", function(event) {

            if (selectedRating < 0.5) {
                event.preventDefault();
                ratingLabel.textContent = "Please select a star rating.";
            }

        });
    }

});