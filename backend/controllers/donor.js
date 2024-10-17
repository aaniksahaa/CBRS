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

  try {
    const donors = await prisma.donor.findMany({
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
    return donor;
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

module.exports = {
  getSingleDonor,
  getDonors,
  createDonor,
  updateDonor,
  deleteDonor,
  deleteDonorPermanent,
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