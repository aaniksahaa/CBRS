const { PrismaClient } = require("@prisma/client");
const prisma = new PrismaClient();

const createVideo = async (payload) => {
  try {
    const video = await prisma.video.create({
      data: {
        author_user_id: payload.user_id,
        lesson_id: payload.lesson_id,
        title: payload.title,
        subtitle: payload.subtitle,
        description: payload.description,
        url: payload.url,
      },
      include: {},
    });

    const response = {
      success: true,
      video_id: video.id,
      // video: video,
    };

    return response;
  } catch (err) {
    console.error(err);
    throw err;
  }
};

const updateVideo = async (payload) => {
  const video_id = payload.id;
  try {
    const video = await prisma.video.update({
      where: {
        id: video_id,
      },
      data: {
        lesson_id: payload.lesson_id,
        title: payload.title,
        subtitle: payload.subtitle,
        description: payload.description,
        url: payload.url,
      },
      include: {},
    });

    const response = {
      success: true,
      video_id: video.id,
      // video: video,
    };

    return response;
  } catch (err) {
    console.error(err);
    throw err;
  }
};

module.exports = { createVideo, updateVideo };
