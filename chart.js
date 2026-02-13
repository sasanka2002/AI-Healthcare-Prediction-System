// STEP 2.1: Get the canvas
const ctx = document.getElementById('myChart');

// STEP 2.2: Create chart
new Chart(ctx, {
    type: 'bar',
    data: {
        labels: ['Diabetes', 'Flu', 'Heart'],
        datasets: [{
            label: 'Disease Count',
            data: [5, 3, 2],
            borderWidth: 1
        }]
    },
    options: {
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});
