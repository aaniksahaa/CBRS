const { PrismaClient } = require('@prisma/client');
const fs = require('fs');
const path = require('path');

const { getDonors } = require('./donor');

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

    console.log(`Donor statistic has been written to: ${filePath}`);
    return filePath;
  } catch (error) {
    console.error('Error generating CSV:', error);
    throw error;
  }
};

async function generateResponseStatCSV() {
  const prisma = new PrismaClient();
  
  try {
    // Get all confirmed responses with their related data
    const responses = await prisma.response.findMany({
      where: {
        // hasConfirmed: true,
      },
      include: {
        notification: {
          include: {
            bloodrequest: true,
          },
        },
      },
    });

    // console.log(responses);

    // Process the data and calculate times
    const statistics = responses.map(response => {
      const a = response.notification.bloodrequest.messageSentAt;
      const b = response.notification.bloodrequest.createdAt;
      const c = response.notification.createdAt;
      const d = response.createdAt;

      // Skip entries where messageSentAt is null
      if (!a) {
        return null;
      }

      // Convert times to seconds from messageSentAt
      const parsingTimeFromStart = (b.getTime() - a.getTime()) / 1000;
      const notificationTimeFromStart = (c.getTime() - a.getTime()) / 1000;
      const responseTimeFromStart = (d.getTime() - a.getTime()) / 1000;
      const parsingTime = (b.getTime() - a.getTime()) / 1000;
      const retrievalTime = (c.getTime() - b.getTime()) / 1000;
      const responseTime = (d.getTime() - c.getTime()) / 1000;

      return {
        messageSentAt: a.toISOString(),
        bloodRequestCreatedAt: b.toISOString(),
        notificationCreatedAt: c.toISOString(),
        responseCreatedAt: d.toISOString(),
        parsingTimeFromStart,
        notificationTimeFromStart,
        responseTimeFromStart,
        parsingTime,
        retrievalTime,
        responseTime
      };
    }).filter(stat => stat !== null); // Remove any entries with null messageSentAt

    // Create CSV content
    const headers = [
      'messageSentAt',
      'bloodRequestCreatedAt',
      'notificationCreatedAt',
      'responseCreatedAt',
      'parsingTimeFromStart',
      'notificationTimeFromStart',
      'responseTimeFromStart',
      'parsingTime',
      'retrievalTime',
      'responseTime'
    ];

    const csvContent = [
      headers.join(','),
      ...statistics.map(stat => [
        stat.messageSentAt,
        stat.bloodRequestCreatedAt,
        stat.notificationCreatedAt,
        stat.responseCreatedAt,
        stat.parsingTimeFromStart,
        stat.notificationTimeFromStart,
        stat.responseTimeFromStart,
        stat.parsingTime,
        stat.retrievalTime,
        stat.responseTime
      ].join(','))
    ].join('\n');

    // Write to file
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filePath = path.join('./statistics', `response-statistics-${timestamp}.csv`);
    fs.writeFileSync(filePath, csvContent);

    console.log(`Response Statistics have been written to: ${filePath}`);

    return {
      filePath,
      totalRecords: statistics.length,
      averageParsingTime: statistics.reduce((acc, stat) => acc + stat.parsingTimeFromStart, 0) / statistics.length,
      averageNotificationTime: statistics.reduce((acc, stat) => acc + stat.notificationTimeFromStart, 0) / statistics.length,
      averageResponseTime: statistics.reduce((acc, stat) => acc + stat.responseTimeFromStart, 0) / statistics.length,
    };

  } catch (error) {
    console.error('Error generating statistics:', error);
    throw error;
  } finally {
    await prisma.$disconnect();
  }
}

module.exports = {generateDonorCSV, generateResponseStatCSV};