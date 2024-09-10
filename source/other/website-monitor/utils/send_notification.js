function sendNotification(message) {
    return fetch('https://gate.whapi.cloud/messages/text', {
        method: 'POST',
        headers: {
            'accept': 'application/json',
            'authorization': 'Bearer ...',
            'content-type': 'application/json'
        },
        body: JSON.stringify({
            "typing_time": 0,
            "to": "995551185124",
            "body": message
        })
    })
        .then(response => response.json())
        .then(data => {
            console.log('Notification sent successfully:', data);
            return data;
        })
        .catch(error => {
            console.error('Error sending notification:', error);
            throw error;
        });
}

globalThis.sendNotification = sendNotification; // to make it available from the content script