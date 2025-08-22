document.addEventListener("DOMContentLoaded", async function () {
  const ctx = document.getElementById("myChart").getContext("2d");

  try {
    const response = await fetch("/events/cycle-length");
    if (!response.ok) throw new Error("Failed to fetch cycle lengths");

    const data = await response.json();

    // Extract labels (months) and values (average cycle length)
    const labels = data.map(item => item.month);
    const values = data.map(item => item.avg_cycle_length);

    new Chart(ctx, {
      type: "line",
      data: {
        labels: labels,
        datasets: [{
          label: "Average Cycle Length (days)",
          fill: false,
          lineTension: 0,
          backgroundColor: "rgba(0,0,255,1.0)",
          borderColor: "rgba(0,0,255,0.5)",
          data: values
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { display: true }
        },
        scales: {
          y: {
            min: 6,
            max: 40,
            title: {
              display: true,
              text: "Days"
            }
          },
          x: {
            title: {
              display: true,
              text: "Month"
            }
          }
        }
      }
    });
  } catch (error) {
    console.error("Error loading cycle length chart:", error);
    ctx.font = "16px Arial";
    ctx.fillText("Failed to load chart", 50, 50);
  }
});
