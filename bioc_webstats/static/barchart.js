function plot_bars(canvas_id, year, data) {
  var ctx = document.getElementById(canvas_id).getContext("2d");
  var gradient = ctx.createLinearGradient(0, 0, 0, 400);
  gradient.addColorStop(0, "rgba(255, 0, 0, 0.5)");
  gradient.addColorStop(1, "rgba(0, 0, 255, 0.5)");

  const downloadsList = [];
  const monthList = [];
  const uniqueIpsList = [];

  const maxRows = Math.min(data.length, 12);

  for (let i = 0; i < maxRows; i++) {
    downloadsList.push(data[i].downloads);
    monthList.push(data[i].month);
    uniqueIpsList.push(data[i].unique_ips);
  }
  var theChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: monthList,
      datasets: [
        {
          label: "Distinct IPs",
          data: uniqueIpsList,
          backgroundColor: '#aaaaff',
          borderWidth: 1,
        },
        {
          label: "Downloads",
          data: downloadsList,
          backgroundColor: '#ddddff',
          borderWidth: 1,
        },
      ],
    },
    options: {
      scales: {
        y: {
          type: "logarithmic",
          min: 10,
          ticks: {
            // Generate the labels for each power of ten
            callback: function (value, index, values) {
              // Return the value if it's an exact power of ten
              if (Math.log10(value) % 1 === 0) {
                return value.toString();
              }
            },
          },
        },
      },
    },
  });
}

document.addEventListener("DOMContentLoaded", (event) => {
  const elements = document.getElementsByClassName("barchart");
  for (let i = 0; i < elements.length; i++) {
    const canvas_id = elements[i].id;
    const year = canvas_id.replace("barchart_", "");
    plot_bars(canvas_id, year, data_table[year]);
  }
});
