const checkServerStatus = async () => {
    try {
      const response = await fetch('YOUR_SERVER_URL_HERE', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json' // Assuming JSON content type, adjust as needed
        },
        body: JSON.stringify({ /* Your request body here */ })
      });
      if (response.ok) {
        console.log('Server is running!');
      } else {
        console.error('Server is not running. Status:', response.status);
      }
    } catch (error) {
      console.error('Error occurred while checking server status:', error);
    }
  };
  
  checkServerStatus();
  