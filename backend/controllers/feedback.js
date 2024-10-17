const { PrismaClient } = require("@prisma/client");
const prisma = new PrismaClient();

const getFeedbacks = async (payload) => {
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

    const feedbacks = await prisma.feedback.findMany({
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
          include: {
            user: true,
          },
        },
      },
    });

    return feedbacks;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

// const createFeedback = async (payload) => {
//   try {
//     const feedback = await prisma.feedback.create({
//       data: {
//         user_id: payload.user_id,
//         is_starred: payload.is_starred, // optional
//         rating: payload.rating,
//         progress: payload.progress, // optional
//         lesson_id: payload.lesson_id, // optional
//         question_id: payload.question_id, // optional
//         geoview_id: payload.geoview_id, // optional
//         video_id: payload.video_id, // optional
//       },
//       include: {
//         user: true,
//         // lesson: true,
//         // question: true,
//         // geoview: true,
//         // video: true,
//       },
//     });

//     const response = {
//       success: true,
//       // feedback: feedback,
//     };

//     return response;
//   } catch (err) {
//     console.error(err);
//     throw err;
//   }
// };

const createFeedback = async (payload) => {
  try {
    // Find existing feedback
    const existingFeedback = await prisma.feedback.findFirst({
      where: {
        user_id: payload.user_id,
        lesson_id: payload.lesson_id,
        question_id: payload.question_id,
        geoview_id: payload.geoview_id,
        video_id: payload.video_id,
      },
    });

    let feedback;

    if (existingFeedback) {
      // Update existing feedback
      feedback = await prisma.feedback.update({
        where: {
          id: existingFeedback.id,
        },
        data: {
          is_starred: payload.is_starred, // optional
          rating: payload.rating,
          progress: payload.progress, // optional
        },
        include: {
          // user: true,
          // lesson: true,
          // question: true,
          // geoview: true,
          // video: true,
        },
      });
    } else {
      // Create new feedback
      feedback = await prisma.feedback.create({
        data: {
          user_id: payload.user_id,
          is_starred: payload.is_starred, // optional
          rating: payload.rating,
          progress: payload.progress, // optional
          lesson_id: payload.lesson_id, // optional
          question_id: payload.question_id, // optional
          geoview_id: payload.geoview_id, // optional
          video_id: payload.video_id, // optional
        },
        include: {
          // user: true,
          // lesson: true,
          // question: true,
          // geoview: true,
          // video: true,
        },
      });
    }

    const response = {
      success: true,
      // feedback: feedback,
    };

    return response;
  } catch (err) {
    console.error(err);
    throw err;
  }
};

module.exports = { getFeedbacks, createFeedback };
