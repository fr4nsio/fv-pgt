<script>
    import { onMount } from 'svelte';
    import { Chart, registerables } from 'chart.js';
    import { manageChartColorScheme } from '../utils/chartutils.js';

    export let plantId;

    Chart.register(...registerables);

    let chart;
    let batteryData = {
      master: { voltage: 0, percent: 0 },
      slave: { voltage: 0, percent: 0 }
    };

    async function fetchBatteryData(plantId)
    {
        const masterResponse = await fetch(`/plant_battery_system_sensor_reading?plant_id=${plantId}&battery_type=master&latest_reading_seconds=86400`);
        const slaveResponse = await fetch(`/plant_battery_system_sensor_reading?plant_id=${plantId}&battery_type=slave&latest_reading_seconds=86400`);

        if (masterResponse.ok && slaveResponse.ok)
        {
            const masterData = await masterResponse.json();
            const slaveData = await slaveResponse.json();

            /* Per ora impostiamo un range massimo fittizio: sarà da prendere il
             * valore vero dalle specifiche di batteria.
             */
            const max_voltage_range = 400.0;

            /* Calcolo medie master e slave: caso array vuoto, 1 elemento,
             * n elementi
             */
            if (masterData.length === 0) {
                batteryData.master.voltage = 0;
            } else if (masterData.length === 1) {
                batteryData.master.voltage = masterData[0].voltage;
            } else {
                // Handle multiple elements case
                const totalVoltage = masterData.reduce((sum, item) => sum + item.voltage, 0);
                batteryData.master.voltage = totalVoltage / masterData.length;
            }
            batteryData.master.percent = (batteryData.master.voltage / max_voltage_range) * 100;

            if (slaveData.length === 0) {
                batteryData.slave.voltage = 0;
            } else if (slaveData.length === 1) {
                batteryData.slave.voltage = slaveData[0].voltage;
            } else {
                // Handle multiple elements case
                const totalVoltage = slaveData.reduce((sum, item) => sum + item.voltage, 0);
                batteryData.slave.voltage = totalVoltage / slaveData.length;
            }
            batteryData.slave.percent = (batteryData.slave.voltage / max_voltage_range) * 100;


            createChart();
        }
        else
        {
            console.error('Error fetching battery data:', masterResponse.statusText, slaveResponse.statusText);
        }
    }

  // Function to create the chart
  function createChart() {
    const ctx = document.getElementById('batteryChart').getContext('2d');
    const labels = ['BMS', 'Battery'];
    const data = {
      labels: labels,
      datasets: [{
        label: 'Percentuale Batteria (media 24 ore)',
        data: [batteryData.master.percent, batteryData.slave.percent],
        backgroundColor: ['rgba(75, 192, 192, 0.2)', 'rgba(153, 102, 255, 0.2)'],
        borderColor: ['rgba(75, 192, 192, 1)', 'rgba(153, 102, 255, 1)'],
        borderWidth: 1
      }]
    };

    if (chart) {
      chart.destroy(); // Destroy previous chart instance
    }

    let baseOptions = {
        scales: {
          y: {
            beginAtZero: true,
            max: 100 // Assuming percentage
          }
        }
    }

    // Unisco le opzioni.                                                       
    const chartOptions = {                                                      
        ...baseOptions,                                                         
        ...manageChartColorScheme(),                                            
    };

    chart = new Chart(ctx, {
      type: 'bar',
      data: data,
      options: chartOptions,
    });
  }

    // Aggiorna lo stato dopo che l'utente cambia impianto da visualizzare. 
    $: if (plantId) {
        fetchBatteryData(plantId);
    }

  // Fetch data when the component mounts
  onMount(() => {
    fetchBatteryData(plantId);
  });
</script>

<canvas id="batteryChart" width="400" height="200"></canvas>
