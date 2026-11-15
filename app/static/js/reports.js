fetch("/manager/reports/chart-data")
    .then(response => {
        if (!response.ok) {
            throw new Error("Chart data could not be loaded");
        }
        return response.json();
    })
    .then(data => {

        const chartCanvas = document.getElementById("salesChart");

        if (!chartCanvas) {
            return;
        }

        new Chart(chartCanvas, {
            type: "bar",

            data: {
                labels: data.labels,
                datasets: [{
                    label: "Sales (PKR)",
                    data: data.values,
                    backgroundColor: "#2e8064",
                    borderRadius: 7,
                    maxBarThickness: 45
                }]
            },

            options: {
                responsive: true,
                maintainAspectRatio: false,

                plugins: {
                    legend: {
                        display: false
                    }
                },

                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    })
    .catch(error => {
        console.error("Sales chart error:", error);
    });