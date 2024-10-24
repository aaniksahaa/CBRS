// controllers/response.js
const { PrismaClient } = require("@prisma/client");
const prisma = new PrismaClient();

const getSingleResponse = async (payload) => {
  try {
    const response = await prisma.response.findUnique({
      where: {
        id: payload.response_id,
      },
      include: {
        notification: {
          include: {
            donor: true,
            bloodrequest: true,
          },
        },
      },
    });
    return response;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

const getResponses = async (payload) => {
  const page = payload.page || 1;
  const perPage = payload.per_page || 10;
  const sortBy = payload.orderby || "createdAt";
  const sortOrder = payload.ordertype === "desc" ? "desc" : "asc";

  // Dynamically build the filters object
  const filters = {};

  if (payload.notificationId) {
    filters.notificationId = payload.notificationId;
  }

  if (payload.hasConfirmed !== undefined) {
    filters.hasConfirmed = payload.hasConfirmed === 'true';
  }

  // Add deleted records filter
  if (!payload.includeDeleted) {
    filters.deletedAt = null;
  }

  try {
    const responses = await prisma.response.findMany({
      where: filters,
      include: {
        notification: {
          include: {
            donor: true,
            bloodrequest: true,
          },
        },
      },
      take: perPage,
      skip: (page - 1) * perPage,
      orderBy: {
        [sortBy]: sortOrder,
      },
    });

    return responses;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

const createResponse = async (payload) => {
  try {
    // Check if response already exists for this notification
    const existingResponse = await prisma.response.findFirst({
      where: { notificationId: payload.notificationId }
    });

    if (existingResponse) {
      throw new Error('Response already exists for this notification');
    }

    const response = await prisma.response.create({
      data: {
        message: payload.message,
        hasConfirmed: payload.hasConfirmed,
        notificationId: payload.notificationId,
      },
      include: {
        notification: {
          include: {
            donor: true,
            bloodrequest: true,
          },
        },
      },
    });

    return {
      success: true,
      response: response,
    };
  } catch (error) {
    console.error(error);
    throw error;
  }
};

const updateResponse = async (payload) => {
  try {
    const response = await prisma.response.update({
      where: {
        id: payload.response_id,
      },
      data: {
        message: payload.message,
        hasConfirmed: payload.hasConfirmed,
        updatedAt: new Date(),
      },
      include: {
        notification: {
          include: {
            donor: true,
            bloodrequest: true,
          },
        },
      },
    });
    
    return {
      success: true,
      response: response,
    };
  } catch (error) {
    console.error(error);
    throw error;
  }
};

const deleteResponse = async (payload) => {
  try {
    const response = await prisma.response.update({
      where: {
        id: payload.response_id,
      },
      data: {
        deletedAt: new Date(),
      },
      include: {
        notification: {
          include: {
            donor: true,
            bloodrequest: true,
          },
        },
      },
    });
    return response;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

const deleteResponsePermanent = async (payload) => {
  try {
    const response = await prisma.response.delete({
      where: {
        id: payload.response_id,
      },
    });
    return response;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

module.exports = {
  getSingleResponse,
  getResponses,
  createResponse,
  updateResponse,
  deleteResponse,
  deleteResponsePermanent,
};