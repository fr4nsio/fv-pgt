<script>
    import { onMount, onDestroy } from 'svelte';
    import { writable } from 'svelte/store';
    import { fetchResource } from '../utils/formUtils.js';
    import { fetchResourceDetails, formatTimestamp } from '../utils/showUtils.js';

    const ticketList = writable([]);
    let interval;
    let plantDetails = {};
    let alarmDetails = {};
    let loading = true;


    async function fetchTickets() 
    {
        const data = await fetchResource('/ticket');
        ticketList.set(data);
    }

    async function fetchPlantDetails(plantId)
    {
        return await fetchResourceDetails('/plant', `${plantId}`);
    }

    async function fetchAlarmDetails(alarmId)
    {
        return await fetchResourceDetails('/alarm', `${alarmId}`);
    }

    async function fetchAllPlantDetails()
    {
        loading = true;
        try {
            const tickets = $ticketList;

            for (let i = 0; i < tickets.length; i++)
            {
                const ticket = tickets[i];
                const plant_id = ticket.plant_id;
                let alarm_id = 0;

                if (ticket.alarms.length > 0)
                    alarm_id = ticket.alarms[0];

                if (!plantDetails[plant_id])
                    plantDetails[plant_id] = await fetchPlantDetails(plant_id);
                if (alarm_id != 0 && !alarmDetails[alarm_id])
                {

                    // Abbiamo bisogno solo delle informazioni dell'allarme
                    // con timestamp più recente. Questo elemento sarà il primo
                    // della lista di ticket.alarms che contiene gli id degli
                    // allarmi.
                    alarmDetails[alarm_id] = await fetchAlarmDetails(alarm_id);
                }
            }

        } catch (error) {
            console.error('Error fetching plant or alarm details:', error);
        } finally {
            // Una volta caricati i dati non serve più la dicitura `loading`.
            loading = false;
        }
    }

    onMount(async () => {
        await fetchTickets();
        await fetchAllPlantDetails();

        interval = setInterval(async() => {
            await fetchTickets();
            await fetchAllPlantDetails();
        }, 5000);
    });

    onDestroy(() => {
        clearInterval(interval);
    });

    // Vedi "Compare Function"
    // https://www.w3schools.com/js/js_array_sort.asp
    // E' simile al qsort del C.
    // Ordine decrescente.
    let sortedTickets = [];
    function sortTickets(tickets)
    {
        return tickets.slice().sort((a, b) => {
            const timestampA = new Date(alarmDetails[a.alarms[0]]?.timestamp).getTime() || 0;
            const timestampB = new Date(alarmDetails[b.alarms[0]]?.timestamp).getTime() || 0;
            return timestampB - timestampA;
        });
    }

    async function updateTicketStatus(ticketId, selectedStatus, event)
    {
        // Controlla se è stato passato uno stato valido. Se è `undefined`
        // non ignora l'operazione.
        if (!selectedStatus)
            return;

        try
        {
            const response = await fetch(`/ticket/${ticketId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ status: selectedStatus }),
            });

            if (!response.ok)
            {
                throw new Error('Network response was not ok');
            }

            // Aggiorna la lista dei ticket in modo che il ticket modificato
            // rifletta il nuovo stato
            await fetchTickets();
        }
        catch (error)
        {
            console.error('Error updating ticket:', error);
        }
    }

    // Aggiorna la lista ordinata ogni volta che la lista originale si
    // aggiorna.
    $: sortedTickets = sortTickets($ticketList);
</script>

<h3>Ticket</h3>
{#if $ticketList.length > 0}
    <table>
        <thead>
            <tr>
                <th>ID</th>
                <th>Nome impianto</th>
                <th>UUID impianto</th>
                <th>Installatore</th>
                <th>Timestamp (UTC)</th>
                <th>Descrizione</th>
                <th>Codice</th>
                <th>Gravità</th>
                <th>Stato</th>
            </tr>
        </thead>
        <tbody>
            {#each sortedTickets as ticket}
                <tr>
                    <td>{ticket.id}</td>
                    <td>{plantDetails[ticket.plant_id]?.name || 'Loading...'}</td>
                    <td>{plantDetails[ticket.plant_id]?.uuid || 'Loading...'}</td>
                    <td>{plantDetails[ticket.plant_id]?.installer || 'Loading...'}</td>
                    <td>{formatTimestamp(alarmDetails[ticket.alarms[0]]?.timestamp || 'Loading...')}</td>
                    <td>{alarmDetails[ticket.alarms[0]]?.description || 'Loading...'}</td>
                    <td>{alarmDetails[ticket.alarms[0]]?.code || 'Loading...'}</td>
                    <td>{alarmDetails[ticket.alarms[0]]?.severity_level || 'Loading...'}</td>
                    <td>
                        <div>
                            <span
                                style="background-color: {ticket.code === 'RESOLVED' ? '#99e699' : 
                                                 ticket.code === 'IN PROGRESS' ? '#bfbfbf' : 
                                                 ticket.code === 'NOT RESOLVED' ? '#ff8080' : 
                                                 'transparent'}"
                            >
                                {ticket.code || 'No status selected'}
                            </span>
                            <select on:change={(e) => updateTicketStatus(ticket.id, e.target.value, e)}>
                                <option value="">Modifica</option>
                                <option value="RESOLVED">RESOLVED</option>
                                <option value="IN PROGRESS">IN PROGRESS</option>
                                <option value="NOT RESOLVED">NOT RESOLVED</option>
                            </select>
                        </div>
                    </td>
                </tr>
            {/each}
        </tbody>
    </table>
{:else}
    <p>Caricamento...</p>
{/if}
