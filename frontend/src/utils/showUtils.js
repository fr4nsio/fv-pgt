export async function fetchResourceDetails(endpoint, id) {
    try {
        const response = await fetch(`${endpoint}/${id}`);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching resource:', error);
        throw error;
    }
}

// Semplicissima funzione per rendere la lettura del timestamp più semplice.
export function formatTimestamp(ts)
{
    if (ts)
        return ts.replace('T', ' ').replace('Z', '');
    else
        return "?";                                     
}
