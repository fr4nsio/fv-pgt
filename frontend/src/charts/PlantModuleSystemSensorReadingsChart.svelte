<script>
  import { onMount, onDestroy } from 'svelte';
  import { Chart, registerables } from 'chart.js';
  import { manageChartColorScheme } from '../utils/chartutils.js';

  export let plantId;

  Chart.register(...registerables);

  let chart;
  let sensorReadings;
  resetSensorReadings();

    const chart_x_intervals = 12;
    function resetSensorReadings()
    {

        const chart_x_intervals = 12;
        let now = Date.now();

        sensorReadings = {
            AC: {
                voltage: Array(chart_x_intervals).fill(null), // Initialize with 12 points
                current: Array(chart_x_intervals).fill(null),
                frequency: Array(chart_x_intervals).fill(null),
                counts: Array(chart_x_intervals).fill(0), // To count how many readings per interval
                timestamps: Array.from({ length: chart_x_intervals }, (_, i) => new Date(now - (i * 2 * 60 * 60 * 1000)).toLocaleTimeString()).reverse()
            },
            DC: {
                voltage: Array(chart_x_intervals).fill(null),
                current: Array(chart_x_intervals).fill(null),
                counts: Array(chart_x_intervals).fill(0),
                timestamps: Array.from({ length: chart_x_intervals }, (_, i) => new Date(now - (i * 2 * 60 * 60 * 1000)).toLocaleTimeString()).reverse()
            }
        };
  }

    async function fetchSensorReadings() {
        resetSensorReadings();
        const response = await fetch(`/plant_module_system_sensor_reading?plant_id=${plantId}&latest_reading_seconds=86400`);

        if (response.ok)
        {
            const data = await response.json();
            processSensorReadings(data);
            createChart();
        }
        else
        {
          console.error('Error fetching sensor readings:', response.statusText);
        }
    }

    function processSensorReadings(data) 
    {
        const chart_x_intervals = 12;
        data.forEach((reading) => {
            const { voltage, current, frequency, timestamp } = reading;
            const now = Date.now();
            const readingTime = new Date(timestamp);
            const readingTimeUTC = readingTime.getTime();

            // I timestamps sono in ms dell'epoch time
            const hoursAgo = Math.floor((now - readingTimeUTC) / (1000 * 3600));

            // Seleziona l'intervallo di riferimento
            // Determine which interval the reading falls into
            // Intervalli di 2 ore.
            const intervalIndex = chart_x_intervals - Math.floor(hoursAgo / 2) - 1;

            if (intervalIndex >= 0 && intervalIndex < chart_x_intervals)
            {
                if (frequency === 0.0)
                {
                    sensorReadings.DC.voltage[intervalIndex] += voltage;
                    sensorReadings.DC.current[intervalIndex] += current;
                    sensorReadings.DC.counts[intervalIndex] += 1; // Count readings for averaging
                }
                else
                {
                    sensorReadings.AC.voltage[intervalIndex] += voltage;
                    sensorReadings.AC.current[intervalIndex] += current;
                    sensorReadings.AC.frequency[intervalIndex] += frequency;
                    sensorReadings.AC.counts[intervalIndex] += 1; // Count readings for averaging
                }
            }
        });

        // Average the values for each interval
        for (let i = 0; i < chart_x_intervals; i++)
        {
            if (sensorReadings.DC.counts[i] > 0)
            {
                sensorReadings.DC.voltage[i] /= sensorReadings.DC.counts[i];
                sensorReadings.DC.current[i] /= sensorReadings.DC.counts[i];
            }
            else
            {
                sensorReadings.DC.voltage[i] = null; // Set to null if no readings
                sensorReadings.DC.current[i] = null; // Set to null if no readings
            }

            if (sensorReadings.AC.counts[i] > 0)
            {
                sensorReadings.AC.voltage[i] /= sensorReadings.AC.counts[i];
                sensorReadings.AC.current[i] /= sensorReadings.AC.counts[i];
                sensorReadings.AC.frequency[i] /= sensorReadings.AC.counts[i];
            }
            else
            {
                sensorReadings.AC.voltage[i] = null;
                sensorReadings.AC.current[i] = null;
                sensorReadings.AC.frequency[i] = null; 
            }
        }
    }

  function createChart() {
    const ctx = document.getElementById('sensorReadingsChart').getContext('2d');

    const data = {
      labels: sensorReadings.AC.timestamps, // Use timestamps for x-axis
      datasets: [
        {
          label: 'AC Voltage',
          data: sensorReadings.AC.voltage,
          borderColor: 'rgba(75, 192, 192, 1)',
          fill: false,
        },
        {
          label: 'AC Current',
          data: sensorReadings.AC.current,
          borderColor: 'rgba(153, 102, 255, 1)',
          fill: false,
        },
        {
          label: 'AC Frequency',
          data: sensorReadings.AC.frequency,
          borderColor: 'rgba(255, 206, 86, 1)',
          fill: false,
        },
        {
          label: 'DC Voltage',
          data: sensorReadings.DC.voltage,
          borderColor: 'rgba(255, 99, 132, 1)',
          fill: false,
        },
        {
          label: 'DC Current',
          data: sensorReadings.DC.current,
          borderColor: 'rgba(54, 162, 235, 1)',
          fill: false,
        }
      ]
    };

    if (chart) {
      chart.destroy(); // Destroy previous chart instance
    }

    let baseOptions = {
        responsive: true,
        plugins: {
          legend: {
            position: 'top',
          },
          tooltip: {
            callbacks: {
              label: function(tooltipItem) {
                return `${tooltipItem.dataset.label}: ${tooltipItem.raw}`;
              }
            }
          }
        },
        scales: {
          x: {
            title: {
              display: true,
              text: 'Tempo (Ultime 24 ore)'
            },
            ticks: {
              autoSkip: true,
              maxTicksLimit: 12 // Limit to 12 intervals
            }
          },
          y: {
            title: {
              display: true,
              text: 'Value'
            }
          }
        }
    }

    // Unisco le opzioni.
    const chartOptions = {
        ...baseOptions,
        ...manageChartColorScheme(),
    };

    chart = new Chart(ctx, {
      type: 'line', // Line chart
      data: data,
      options: chartOptions,
    });
  }

  let interval;

  // Update the state after the user changes the plant to display.
  $: if (plantId) {
    fetchSensorReadings();
    clearInterval(interval);
    interval = setInterval(fetchSensorReadings, 300 * 1000);
  }

  onDestroy(() => {
    clearInterval(interval);
  });
</script>

<canvas id="sensorReadingsChart" width="400" height="300"></canvas>
