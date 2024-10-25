const { PrismaClient } = require('@prisma/client');
const fs = require('fs');
const path = require('path');

async function generateStatistics() {
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

    console.log(responses);

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

      return {
        messageSentAt: a.toISOString(),
        bloodRequestCreatedAt: b.toISOString(),
        notificationCreatedAt: c.toISOString(),
        responseCreatedAt: d.toISOString(),
        parsingTimeFromStart,
        notificationTimeFromStart,
        responseTimeFromStart,
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
      'responseTimeFromStart'
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
        stat.responseTimeFromStart
      ].join(','))
    ].join('\n');

    // Write to file
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filePath = path.join('./statistics', `response-statistics-${timestamp}.csv`);
    fs.writeFileSync(filePath, csvContent);

    console.log(`Statistics have been written to: ${filePath}`);

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

module.exports = generateStatistics;