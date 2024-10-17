const { PrismaClient } = require("@prisma/client");
const prisma = new PrismaClient();

const createComment = async (payload) => {
  try {
    const comment = await prisma.comment.create({
      data: {
        user_id: payload.user_id,
        post_id: payload.post_id,
        text: payload.text,
        image_urls: payload.image_urls, // optional
      },
      include: {
        user: true,
      },
    });

    const response = {
      success: true,
      comment_id: comment.id,
      // comment: comment,
    };

    return response;
  } catch (err) {
    console.error(err);
    throw err;
  }
};

module.exports = { createComment };
