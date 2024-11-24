// Check if any grocery items are below the threshold weight and update the notification
window.onload = function() {
    const thresholdWeight = 100; // 100g
    const groceries = [
        { id: 1, name: 'Apple', weight: 50, expiry: '2024-12-01' },
        { id: 2, name: 'Banana', weight: 150, expiry: '2024-12-05' },
        { id: 3, name: 'Carrot', weight: 80, expiry: '2024-12-10' },
        // Add more groceries here
    ];

    // Check if any grocery has a weight less than the threshold
    const lowStockGroceries = groceries.filter(grocery => grocery.weight < thresholdWeight);

    // Get the notification message element to update the notification text
    const notificationMessage = document.getElementById('notification-message');
    
    if (lowStockGroceries.length > 0) {
        // Display the names of groceries below the threshold weight in the notification
        notificationMessage.textContent = 'Stock below 100g: ' + lowStockGroceries.map(g => g.name).join(', ');
    } else {
        // Display a message if all stock is above the threshold
        notificationMessage.textContent = 'All stock is above 100g.';
    }

    // Set up click event to show stock alerts when the notification icon is clicked
    document.getElementById('notification-icon').addEventListener('click', function() {
        if (lowStockGroceries.length > 0) {
            // Show an alert with the names of groceries below the threshold
            const lowStockNames = lowStockGroceries.map(g => g.name).join(', ');
            alert('You have stock alerts for: ' + lowStockNames);
        } else {
            // If no groceries are below the threshold, show a general notification
            alert('All stock is above 100g.');
        }
    });
};