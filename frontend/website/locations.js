async function loadLocations() {
    const status = document.getElementById('locationsStatus');
    const list = document.getElementById('locationsList');

    try {
        const response = await fetch('/api/locations');
        if (!response.ok) {
            throw new Error(`Request failed with status ${response.status}`);
        }

        const data = await response.json();
        for (const location of data.locations) {
            const item = document.createElement('li');
            const name = document.createElement('strong');
            name.textContent = `${location.name} (${location.type})`;
            item.append(name, document.createElement('br'));

            const address = document.createElement('span');
            address.textContent = `${location.address}, ${location.city}, ${location.state} ${location.postal_code}`;
            item.append(address);

            const services = document.createElement('p');
            services.textContent = `Services: ${location.services.join(', ')}`;
            item.append(services);
            list.append(item);
        }

        status.textContent = data.locations.length
            ? ''
            : 'No locations are currently available.';
    } catch (error) {
        console.error('Unable to load locations:', error);
        status.textContent = 'Locations are unavailable right now. Please try again later.';
    }
}

document.addEventListener('DOMContentLoaded', loadLocations);
