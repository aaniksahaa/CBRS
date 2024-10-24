// controllers/notification.js
const { PrismaClient } = require("@prisma/client");
const prisma = new PrismaClient();

const getSingleNotification = async (payload) => {
  try {
    const notification = await prisma.notification.findUnique({
      where: {
        id: payload.notification_id,
      },
      include: {
        donor: true,
        bloodrequest: true,
      },
    });
    return notification;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

const getNotifications = async (payload) => {
  const page = payload.page || 1;
  const perPage = payload.per_page || 10;
  const sortBy = payload.orderby || "createdAt";
  const sortOrder = payload.ordertype === "desc" ? "desc" : "asc";

  // Dynamically build the filters object
  const filters = {};

  if (payload.donorId) {
    filters.donorId = payload.donorId;
  }

  if (payload.bloodrequestId) {
    filters.bloodrequestId = payload.bloodrequestId;
  }

  if (payload.telegramMessageId) {
    filters.telegramMessageId = payload.telegramMessageId;
  }

  // Add deleted records filter
  if (!payload.includeDeleted) {
    filters.deletedAt = null;
  }

  try {
    const notifications = await prisma.notification.findMany({
      where: filters,
      include: {
        donor: true,
        bloodrequest: true,
      },
      take: perPage,
      skip: (page - 1) * perPage,
      orderBy: {
        [sortBy]: sortOrder,
      },
    });

    return notifications;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

const createNotification = async (payload) => {
  try {
    const notification = await prisma.notification.create({
      data: {
        telegramMessageId: payload.telegramMessageId,
        donorId: payload.donorId,
        bloodrequestId: payload.bloodrequestId,
      },
      include: {
        donor: true,
        bloodrequest: true,
      },
    });

    const response = {
      success: true,
      notification: notification,
    };

    return response;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

const updateNotification = async (payload) => {
  try {
    const notification = await prisma.notification.update({
      where: {
        id: payload.notification_id,
      },
      data: {
        telegramMessageId: payload.telegramMessageId,
        donorId: payload.donorId,
        bloodrequestId: payload.bloodrequestId,
        updatedAt: new Date(),
      },
      include: {
        donor: true,
        bloodrequest: true,
      },
    });
    
    const response = {
      success: true,
      notification: notification,
    };

    return response;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

const deleteNotification = async (payload) => {
  try {
    const notification = await prisma.notification.update({
      where: {
        id: payload.notification_id,
      },
      data: {
        deletedAt: new Date(),
      },
      include: {
        donor: true,
        bloodrequest: true,
      },
    });
    return notification;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

const deleteNotificationPermanent = async (payload) => {
  try {
    const notification = await prisma.notification.delete({
      where: {
        id: payload.notification_id,
      },
    });
    return notification;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

module.exports = {
  getSingleNotification,
  getNotifications,
  createNotification,
  updateNotification,
  deleteNotification,
  deleteNotificationPermanent,
};