const { PrismaClient } = require("@prisma/client");
const prisma = new PrismaClient();

const getSingleBloodrequest = async (payload) => {
  try {
    const bloodrequest = await prisma.bloodrequest.findUnique({
      where: {
        id: payload.bloodrequest_id,
      },
      include: {
        contacts: true,
        notifications: true,
      },
    });
    return bloodrequest;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

const getBloodrequests = async (payload) => {
  const page = payload.page || 1;
  const perPage = payload.per_page || 10;
  const sortBy = payload.orderby || "createdAt";
  const sortOrder = payload.ordertype === "desc" ? "desc" : "asc";

  try {
    const bloodrequests = await prisma.bloodrequest.findMany({
      take: perPage,
      skip: (page - 1) * perPage,
      orderBy: {
        [sortBy]: sortOrder,
      },
      include: {
        contacts: true,
        notifications: true,
      },
      where: {
        deletedAt: null, // Only get non-deleted requests by default
      },
    });

    return bloodrequests;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

const createBloodrequest = async (payload) => {
  try {
    const bloodrequest = await prisma.bloodrequest.create({
      data: {
        sourceTelegramChatId: payload.sourceTelegramChatId,
        sourceTelegramMessageId: payload.sourceTelegramMessageId,
        sourceDiscordChannelId: payload.sourceDiscordChannelId,
        messageText: payload.messageText,
        bloodGroup: payload.bloodGroup,
        bagsNeeded: payload.bagsNeeded,
        patientName: payload.patientName,
        patientGender: payload.patientGender,
        patientAgeGroup: payload.patientAgeGroup,
        condition: payload.condition,
        location: payload.location,
        latitude: payload.latitude,
        longitude: payload.longitude,
        hospitalName: payload.hospitalName,
        locationMarkers: payload.locationMarkers || [],
        probableDay: payload.probableDay,
        probableTime: payload.probableTime,
        transportation: payload.transportation,
        allowance: payload.allowance,
        contacts: {
          create: payload.contacts.map(contact => ({
            name: contact.name,
            numbers: contact.numbers,
            relationWithPatient: contact.relationWithPatient,
          })),
        },
      },
      include: {
        contacts: true,
        notifications: true,
      },
    });

    const response = {
      success: true,
      bloodrequest: bloodrequest,
    };

    return response;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

const updateBloodrequest = async (payload) => {
  try {
    // First, delete existing contacts if we're updating them
    if (payload.contacts) {
      await prisma.contact.deleteMany({
        where: {
          bloodrequestId: payload.bloodrequest_id,
        },
      });
    }

    const bloodrequest = await prisma.bloodrequest.update({
      where: {
        id: payload.bloodrequest_id,
      },
      data: {
        sourceTelegramChatId: payload.sourceTelegramChatId,
        sourceTelegramMessageId: payload.sourceTelegramMessageId,
        sourceDiscordChannelId: payload.sourceDiscordChannelId,
        messageText: payload.messageText,
        bloodGroup: payload.bloodGroup,
        bagsNeeded: payload.bagsNeeded,
        patientName: payload.patientName,
        patientGender: payload.patientGender,
        patientAgeGroup: payload.patientAgeGroup,
        condition: payload.condition,
        location: payload.location,
        hospitalName: payload.hospitalName,
        locationMarkers: payload.locationMarkers,
        probableDay: payload.probableDay ? new Date(payload.probableDay) : undefined,
        probableTime: payload.probableTime,
        transportation: payload.transportation,
        allowance: payload.allowance,
        contacts: payload.contacts ? {
          create: payload.contacts.map(contact => ({
            name: contact.name,
            numbers: contact.numbers,
            relationWithPatient: contact.relationWithPatient,
          })),
        } : undefined,
        updatedAt: new Date(),
      },
      include: {
        contacts: true,
        notifications: true,
      },
    });
    return bloodrequest;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

const deleteBloodrequest = async (payload) => {
  try {
    const bloodrequest = await prisma.bloodrequest.update({
      where: {
        id: payload.bloodrequest_id,
      },
      data: {
        deletedAt: new Date(),
      },
      include: {
        contacts: true,
        notifications: true,
      },
    });
    return bloodrequest;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

const deleteBloodrequestPermanent = async (payload) => {
  try {
    const bloodrequest = await prisma.bloodrequest.delete({
      where: {
        id: payload.bloodrequest_id,
      },
      include: {
        contacts: true,
        notifications: true,
      },
    });
    return bloodrequest;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

module.exports = {
  getSingleBloodrequest,
  getBloodrequests,
  createBloodrequest,
  updateBloodrequest,
  deleteBloodrequest,
  deleteBloodrequestPermanent,
};

/**
 * Creating Bloodrequest - POST
 * 
 * {
        "messageText": "Urgent blood needed",
        "bloodGroup": "A+",
        "bagsNeeded": 2,
        "patientName": "John Doe",
        "patientGender": "male",
        "patientAgeGroup": "adult",
        "condition": "surgery",
        "location": "Dhaka",
        "hospitalName": "Square Hospital",
        "locationMarkers": ["Dhaka", "Banani"],
        "probableDay": "2024-03-20",
        "probableTime": "10:00 AM",
        "transportation": "Y",
        "allowance": "Y",
        "sourceTelegramChatId": "123456789",
        "contacts": [
            {
                "name": "Jane Doe",
                "numbers": ["+8801712345678", "+8801812345678"],
                "relationWithPatient": "sister"
            },
            {
                "name": "John Smith",
                "numbers": ["+8801612345678"],
                "relationWithPatient": "friend"
            }
        ]
    }

    Update Bloodrequest - PUT
 * {
        "bloodrequest_id": "6505c87e7a524b867ddd8f83",
        "messageText": "Urgent blood needed - Updated",
        "bloodGroup": "A+",
        "bagsNeeded": 3,
        // ... (same fields as above)
        "contacts": [
            {
                "name": "Jane Doe",
                "numbers": ["+8801712345678", "+8801812345678"],
                "relationWithPatient": "sister"
            }
        ]
    }
 */