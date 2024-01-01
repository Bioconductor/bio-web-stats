function plot_bars(canvas_id, year) {
    console.log(canvas_id); // Add this line
    console.log(year); // Add this line
    var ctx = document
        .getElementById(canvas_id)
        .getContext("2d");
    var gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, 'rgba(255, 0, 0, 0.5)');
    gradient.addColorStop(1, 'rgba(0, 0, 255, 0.5)');
    var unique_ip = [1,2,3,4,5,6,7,8,9,10,11,12];
    var myChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            datasets: [{
                label: 'Unique IP',
                data:  unique_ip,
                backgroundColor: gradient,
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero: true
                    }
                }]
            }
        }
    });
};

console.log("at the fcn");
document.addEventListener('DOMContentLoaded', (event) => {
    const elements = document.getElementsByClassName('barchart');
    for (let i = 0; i < elements.length; i++) {
        const canvas_id = elements[i].id;
        const year = canvas_id.replace('barchart_', '');
        plot_bars(canvas_id, year);
    }
});