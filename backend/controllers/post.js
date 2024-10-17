const { PrismaClient } = require("@prisma/client");
const prisma = new PrismaClient();

const getPosts = async (payload) => {
  const include_all = payload.include_all || false;
  //console.log(include_all)
  try {
    const page = payload.page || 1;
    const perPage = payload.per_page || 10;
    const sortBy = payload.sort_by || "createdAt";
    const sortOrder = payload.sort_type === "asc" ? "asc" : "desc";

    const user_id = payload.user_id;
    const lesson_id = payload.lesson_id;
    const geoview_id = payload.geoview_id;
    const video_id = payload.video_id;
    const question_id = payload.question_id;

    const posts = await prisma.post.findMany({
      take: perPage,
      skip: (page - 1) * perPage,
      orderBy: {
        [sortBy]: sortOrder,
      },
      where: {
        ...(user_id && { user_id }),
        ...(lesson_id && { lesson_id }),
        ...(geoview_id && { geoview_id }),
        ...(video_id && { video_id }),
        ...(question_id && { question_id }),
      },
      include: {
        user: true,
        // lesson: include_all,
        // question: include_all,
        // geoview: include_all,
        // video: include_all,
        comments: {
          orderBy: {
            createdAt: "desc", // Sort comments by created_at date, latest first
          },
          include: {
            user: true,
          },
        },
      },
    });

    return posts;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

const createPost = async (payload) => {
  try {
    const post = await prisma.post.create({
      data: {
        user_id: payload.user_id,
        type: payload.type, // optional
        text: payload.text,
        image_urls: payload.image_urls, // optional
        lesson_id: payload.lesson_id, // optional
        question_id: payload.question_id, // optional
        geoview_id: payload.geoview_id, // optional
        video_id: payload.video_id, // optional
      },
      include: {
        user: true,
        // lesson: true,
        // question: true,
        // geoview: true,
        // video: true,
      },
    });

    const response = {
      success: true,
      post_id: post.id,
      // post: post,
    };

    return response;
  } catch (err) {
    console.error(err);
    throw err;
  }
};

module.exports = { getPosts, createPost };
