const { PrismaClient } = require("@prisma/client");
const prisma = new PrismaClient();

const getSingleDonor = async (payload) => {
  try {
    const donor = await prisma.donor.findUnique({
      where: {
        id: payload.donor_id,
      },
    });
    return donor;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

const getDonors = async (payload) => {
  const page = payload.page || 1;
  const perPage = payload.per_page || 10;
  const sortBy = payload.orderby || "name";
  const sortOrder = payload.ordertype === "desc" ? "desc" : "asc";

  // Dynamically build the filters object
  const filters = {};

  if (payload.chatPlatform) {
    filters.chatPlatform = payload.chatPlatform;
  }
  
  if (payload.telegramUsername) {
    filters.telegramUsername = payload.telegramUsername;
  }

  if (payload.discordUserId) {
    filters.discordUserId = payload.discordUserId;
  }

  if (payload.telegramChatId) {
    filters.telegramChatId = payload.telegramChatId;
  }

  if (payload.bloodGroup) {
    filters.bloodGroup = payload.bloodGroup;
  }

  // Add more filters as needed
  // Example: if filtering by name
  if (payload.name) {
    filters.name = { contains: payload.name, mode: 'insensitive' }; // Partial match and case insensitive
  }

  try {
    const donors = await prisma.donor.findMany({
      where: filters, // Use the dynamic filters object
      take: perPage,
      skip: (page - 1) * perPage,
      orderBy: {
        [sortBy]: sortOrder,
      },
    });

    return donors;
  } catch (error) {
    console.error(error);
    throw error;
  }
};


const createDonor = async (payload) => {
  try {
    const donor = await prisma.donor.create({
      data: {
        name: payload.name,
        firstName: payload.firstName,
        lastName: payload.lastName,
        chatPlatform: payload.chatPlatform,
        telegramUsername: payload.telegramUsername,
        discordUserId: payload.discordUserId,
        telegramChatId: payload.telegramChatId,
        latitude: payload.latitude,
        longitude: payload.longitude,
        lastDonated: payload.lastDonated ? new Date(payload.lastDonated) : null,
        bloodGroup: payload.bloodGroup,
        isNotificationDisabled: payload.isNotificationDisabled || false,
      },
    });

    const response = {
      success: true,
      donor: donor,
    };

    return response;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

const updateDonor = async (payload) => {
  try {
    const donor = await prisma.donor.update({
      where: {
        id: payload.donor_id,
      },
      data: {
        name: payload.name,
        firstName: payload.firstName,
        lastName: payload.lastName,
        chatPlatform: payload.chatPlatform,
        telegramUsername: payload.telegramUsername,
        discordUserId: payload.discordUserId,
        telegramChatId: payload.telegramChatId,
        latitude: payload.latitude,
        longitude: payload.longitude,
        lastDonated: payload.lastDonated ? new Date(payload.lastDonated) : undefined,
        bloodGroup: payload.bloodGroup,
        isNotificationDisabled: payload.isNotificationDisabled,
        updatedAt: new Date(),
      },
    });
    
    const response = {
      success: true,
      donor: donor,
    };

    return response;

  } catch (error) {
    console.error(error);
    throw error;
  }
};

const deleteDonor = async (payload) => {
  try {
    const donor = await prisma.donor.update({
      where: {
        id: payload.donor_id,
      },
      data: {
        deletedAt: new Date(),
      },
    });
    return donor;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

const deleteDonorPermanent = async (payload) => {
  try {
    const donor = await prisma.donor.delete({
      where: {
        id: payload.donor_id,
      },
    });
    return donor;
  } catch (error) {
    console.error(error);
    throw error;
  }
};





// Haversine formula to calculate distance between two points on Earth
function calculateHaversineDistance(lat1, lon1, lat2, lon2) {
  const R = 6371; // Earth's radius in kilometers

  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  
  const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
            Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * 
            Math.sin(dLon/2) * Math.sin(dLon/2);
  
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  const distance = R * c; // Distance in kilometers
  
  return distance;
}

const findProbableDonors = async (payload) => {
  try {
      // THRESHOLD_MONTHS = 4;
      THRESHOLD_DAYS = 120;

      // First, get the blood request details
      const bloodrequest = await prisma.bloodrequest.findUnique({
          where: {
              id: payload.bloodrequest_id
          }
      });

      if (!bloodrequest) {
          throw new Error("Blood request not found");
      }

      if (!bloodrequest.bloodGroup) {
          throw new Error("Blood group not specified in the request");
      }

      // Calculate the date 4 months ago
      const thresholdDate = new Date();
      // thresholdDate.setMonth(thresholdDate.getMonth() - THRESHOLD_MONTHS);
      thresholdDate.setDate(thresholdDate.getDate() - THRESHOLD_DAYS);

      // Get all eligible donors based on blood group and donation history
      const eligibleDonors = await prisma.donor.findMany({
          where: {
              // bloodGroup: bloodrequest.bloodGroup
              AND: [
                  { bloodGroup: bloodrequest.bloodGroup },
                  {
                      OR: [
                          { lastDonated: { lt: thresholdDate } },
                          { lastDonated: null }
                      ]
                  },
                  // { deletedAt: null },
                  { isNotificationDisabled: false }
              ]
          }
      });

      console.log('Eligible Donors:')
      console.log(eligibleDonors);

      // Process donors and calculate distances
      const processedDonors = eligibleDonors.map(donor => {
          if (donor.latitude && donor.longitude && bloodrequest.latitude && bloodrequest.longitude) {
              const distance = calculateHaversineDistance(
                  donor.latitude,
                  donor.longitude,
                  bloodrequest.latitude,
                  bloodrequest.longitude
              );
              return { ...donor, distance };
          }
          return { ...donor, distance: null };
      });

      console.log("Porcessed:")
      console.log(processedDonors);

      // Separate donors with and without location data
      const donorsWithLocation = processedDonors
          .filter(donor => donor.distance !== null)
          .filter(donor => donor.distance <= 40) // Filter donors within 4km
          .sort((a, b) => a.distance - b.distance); // Sort by distance

      const donorsWithoutLocation = processedDonors
          .filter(donor => donor.distance === null);

      // Combine the results
      const result = {
          bloodRequest: {
              id: bloodrequest.id,
              bloodGroup: bloodrequest.bloodGroup,
              location: {
                  latitude: bloodrequest.latitude,
                  longitude: bloodrequest.longitude
              }
          },
          nearbyDonors: donorsWithLocation.map(donor => ({
              id: donor.id,
              name: donor.name,
              bloodGroup: donor.bloodGroup,
              distance: Number(donor.distance.toFixed(2)), // Round to 2 decimal places
              lastDonated: donor.lastDonated,
              chatPlatform: donor.chatPlatform,
              telegramUsername: donor.telegramUsername,
              discordUserId: donor.discordUserId,
              telegramChatId: donor.telegramChatId
          })),
          otherEligibleDonors: donorsWithoutLocation.map(donor => ({
              id: donor.id,
              name: donor.name,
              bloodGroup: donor.bloodGroup,
              lastDonated: donor.lastDonated,
              chatPlatform: donor.chatPlatform,
              telegramUsername: donor.telegramUsername,
              discordUserId: donor.discordUserId,
              telegramChatId: donor.telegramChatId
          })),
          stats: {
              totalEligibleDonors: eligibleDonors.length,
              nearbyDonorsCount: donorsWithLocation.length,
              otherEligibleDonorsCount: donorsWithoutLocation.length
          }
      };

      return result;
  } catch (error) {
      console.error("Error in findProbableDonors:", error);
      throw error;
  }
};


module.exports = {
  getSingleDonor,
  getDonors,
  createDonor,
  updateDonor,
  deleteDonor,
  deleteDonorPermanent,
  findProbableDonors
};

/**
 * Creating Donor - POST
 * 
 * {
        "name": "John Doe",
        "firstName": "John",
        "lastName": "Doe",
        "chatPlatform": "telegram",
        "telegramUsername": "johndoe",
        "telegramChatId": "123456789",
        "latitude": 23.8103,
        "longitude": 90.4125,
        "lastDonated": "2024-03-15",
        "bloodGroup": "A+",
        "isNotificationDisabled": false
    }

    Update Donor - PUT
 * {
        "donor_id": "6505c87e7a524b867ddd8f83",
        "name": "John Doe",
        "firstName": "John",
        "lastName": "Doe",
        "chatPlatform": "telegram",
        "telegramUsername": "johndoe",
        "telegramChatId": "123456789",
        "latitude": 23.8103,
        "longitude": 90.4125,
        "lastDonated": "2024-03-15",
        "bloodGroup": "A+",
        "isNotificationDisabled": false
    }
 */