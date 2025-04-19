const fs = require('fs');
const path = require('path');
const { getDonors } = require('./controllers/donor');

const generateDonorCSV = async () => {
  try {
    const donors = await getDonors({per_page: 500});

    // Define the headers
    const headers = ['Name', 'Platform', 'Telegram Username', 'Blood Group', 'Last Donated'];
    
    // Convert donors data to CSV rows
    const rows = donors.map(donor => [
      donor.name,
      donor.chatPlatform,
      donor.telegramUsername ? `@${donor.telegramUsername}` : 'N/A',
      donor.bloodGroup,
      donor.lastDonated 
        ? new Date(donor.lastDonated).toLocaleDateString()
        : 'Never'
    ]);

    // Combine headers and rows
    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.join(','))
    ].join('\n');

    // console.log(csvContent);

    // Create timestamp and filepath
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const directory = './statistics';
    
    // Create directory if it doesn't exist
    if (!fs.existsSync(directory)) {
      fs.mkdirSync(directory, { recursive: true });
    }

    const filePath = path.join(directory, `donor-data-${timestamp}.csv`);
    fs.writeFileSync(filePath, csvContent);

    console.log(`CSV file generated successfully: ${filePath}`);
    return filePath;
  } catch (error) {
    console.error('Error generating CSV:', error);
    throw error;
  }
};

// Update your main function to include CSV generation
const f = async () => {
  try {
    await generateDonorCSV();
  } catch (error) {
    console.error('Error:', error);
  }
};

f();