<script>
    import { onMount, onDestroy } from 'svelte';
    import { writable } from 'svelte/store';

    // Passato come prop.
    export let plantId;

    let dc_voltage = 0, dc_current = 0, ac_voltage = 0, ac_current = 0, ac_frequency = 0;
    let instant_readings_available = false;

    async function fetchSensorReading() {
        const response = await fetch(`/plant_module_system_sensor_reading?plant_id=${plantId}&results=25`);

        if (response.ok) {
            const data = await response.json(); 

            // Resetta sempre i valori nel caso venga tornata una lista vuota
            // dopo aver cambiato impianto visualizzato.
            dc_voltage = 0, dc_current = 0, ac_voltage = 0, ac_current = 0, ac_frequency = 0;

            // C'è bisogno di 1 lettura dc e 1 ac.
            let ac = false;
            let dc = false;

            for (const reading of data) {
                const { voltage, current, frequency } = reading;
                if (frequency === 0.0) {
                    dc_voltage = voltage;
                    dc_current = current;
                    dc = true;
                }
                else {
                    ac_voltage = voltage;
                    ac_current = current;
                    ac_frequency = frequency;
                    ac = true;
                }

                if (ac && dc)
                {
                    instant_readings_available = true;
                    break
                }
            }
        } else {
            console.error('Error fetching sensor readings:', response.statusText);   
        }
    }

    let interval;

    $: if (plantId) {
        fetchSensorReading();
        clearInterval(interval);
        interval = setInterval(fetchSensorReading, 5000);
    }

    onDestroy(() => {
        clearInterval(interval);
    })

    onMount(async () => {
        fetchSensorReading();
        return () => clearInterval(interval);
    });
</script>

<div class="object-details">
    <h3>Valori istantanei</h3>
    <div class="object-details">
        <h3>AC (~)</h3>
        <ul>
            <li><b>Corrente (A):</b> {ac_current.toFixed(2)}</li>
            <li><b>Voltaggio (V):</b> {ac_voltage.toFixed(2)}</li>
            <li><b>Frequenza (Hz):</b> {ac_frequency.toFixed(2)}</li>
        </ul>
    </div>
    <div class="object-details">
        <h3>DC (---)</h3>
        <ul>
            <li><b>Corrente (A):</b> {dc_current.toFixed(2)}</li>
            <li><b>Voltaggio (V):</b> {dc_voltage.toFixed(2)}</li>
        </ul>
    </div>
</div>
