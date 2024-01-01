function plot_bars(canvas_id, year, data) {
    var ctx = document
        .getElementById(canvas_id)
        .getContext("2d");
    var gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, 'rgba(255, 0, 0, 0.5)');
    gradient.addColorStop(1, 'rgba(0, 0, 255, 0.5)');

    // Initialize empty arrays for each element
    const downloadsList = [];
    const monthList = [];
    const uniqueIpsList = [];

    // Define the maximum number of rows to iterate
    const maxRows = Math.min(data.length, 12);

    // Iterate through the data array and populate the lists
    for (let i = 0; i < maxRows; i++) {
        downloadsList.push(data[i].downloads);
        monthList.push(data[i].month);
        uniqueIpsList.push(data[i].unique_ips);
    }

    var unique_ip = [1,2,3,4,5,6,7,8,9,10,11,12];
    var myChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: monthList,
            datasets: [{
                label: 'Unique IPs',
                data: uniqueIpsList,
                backgroundColor: gradient,
                borderWidth: 1
            },
            {
                label: 'Downloads',
                data: downloadsList,
                backgroundColor: gradient,
                borderWidth: 1
            }]
        },
        options: {
        }
    });
};

document.addEventListener('DOMContentLoaded', (event) => {
    const elements = document.getElementsByClassName('barchart');
    for (let i = 0; i < elements.length; i++) {
        const canvas_id = elements[i].id;
        const year = canvas_id.replace('barchart_', '');
        plot_bars(canvas_id, year, data_table[year]);
    }
});