window.onload = function() {
    const thresholdWeight = 100; // 100g threshold for low stock

    // Fetch data from the Flask endpoint that returns data from Firebase
    fetch('/get-load-cell-data')
        .then(response => response.json())
        .then(data => {
            if (data && data.loadCell) {
                // Create an array of load cell objects from the data
                const loadCells = Object.keys(data.loadCell).map(key => ({
                    id: key,
                    weight: data.loadCell[key].weight
                }));

                // Display the weights of all load cells
                loadCells.forEach(loadCell => {
                    document.getElementById(`weight${loadCell.id}`).innerText = `Load Cell ${loadCell.id}: ${loadCell.weight} kg`;
                });

                // Filter load cells below the threshold weight
                const lowStockLoadCells = loadCells.filter(loadCell => loadCell.weight < thresholdWeight);

                // Get the notification message element to update the notification text
                const notificationMessage = document.getElementById('notification-message');

                if (lowStockLoadCells.length > 0) {
                    // Display the IDs and weights of load cells below the threshold in the notification
                    notificationMessage.textContent = 'Load cells below 100g: ' + lowStockLoadCells.map(l => `${l.id} (${l.weight}g)`).join(', ');
                } else {
                    // Display a message if all load cells are above the threshold
                    notificationMessage.textContent = 'All load cells are above 100g.';
                }

                // Set up click event to show stock alerts when the notification icon is clicked
                document.getElementById('notification-icon').addEventListener('click', function() {
                    if (lowStockLoadCells.length > 0) {
                        // Show an alert with the IDs and weights of load cells below the threshold
                        const lowStockDetails = lowStockLoadCells.map(l => `${l.id} (${l.weight}g)`).join(', ');
                        alert('You have stock alerts for: ' + lowStockDetails);
                    } else {
                        // If no load cells are below the threshold, show a general notification
                        alert('All load cells are above 100g.');
                    }
                });
            } else {
                console.log("No data available");
                document.getElementById('notification-message').textContent = 'No load cell data found.';
            }
        })
        .catch(error => {
            console.error("Error fetching data:", error);
            document.getElementById('notification-message').textContent = 'Error fetching data from Firebase.';
        });
};