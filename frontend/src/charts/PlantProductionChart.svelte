<script>
  import { onMount } from 'svelte';
  import { Chart, registerables } from 'chart.js';
  import { fetchResourceDetails } from '../utils/showUtils.js';
  import { manageChartColorScheme } from '../utils/chartutils.js';

  export let plantProductionId;

  Chart.register(...registerables);

  let chart;
  let plantProductionData = {
    daily: 0.0,
    monthly: 0.0
  };

  async function fetchPlantProductionData(plantProductionId)
  {
      const data = await fetchResourceDetails('/plant_production', `${plantProductionId}`);
      plantProductionData.daily = data.daily_kwh;
      plantProductionData.monthly = data.monthly_kwh;
      createChart();
  }

  // Function to create the chart
  function createChart()
  {
    const ctx = document.getElementById('plantProductionChart').getContext('2d');
    const labels = ['Giornaliero', 'Mensile'];
    const data = {
      labels: labels,
      datasets: [{
        label: 'Prodizione Impianto (kWh)',
        data: [plantProductionData.daily, plantProductionData.monthly],
        backgroundColor: ['rgba(75, 192, 192, 0.2)', 'rgba(153, 102, 255, 0.2)'],
        borderColor: ['rgba(75, 192, 192, 1)', 'rgba(153, 102, 255, 1)'],
        borderWidth: 1
      }]
    };

    if (chart) {
      chart.destroy(); // Destroy previous chart instance
    }

    let baseOptions = {
        indexAxis: 'y', // Set indexAxis to 'y' for horizontal bars
        responsive: true,
        scales: {
          x: {
            beginAtZero: true,
            title: {
              display: true,
              text: 'kWh'
            }
          },
          y: {
            title: {
              display: true,
              text: 'Tipo di Produzione'
            }
          }
        },
        plugins: {
          legend: {
            display: false,
          },
          tooltip: {
            callbacks: {
              label: function(tooltipItem) {
                return `${tooltipItem.label}: ${tooltipItem.raw} kWh`;
              }
            }
          },
        }
    }

    // Unisco le opzioni.
    const chartOptions = {
        ...baseOptions,
        ...manageChartColorScheme(),
    };

    chart = new Chart(ctx, {
      type: 'bar', // Keep the type as 'bar'
      data: data,
      options: chartOptions,
    });
  }

  $: if (plantProductionId) {
      fetchPlantProductionData(plantProductionId);
  }

  onMount(() => {
      fetchPlantProductionData(plantProductionId);
  });
</script>

<canvas id="plantProductionChart" width="400" height="150"></canvas>
