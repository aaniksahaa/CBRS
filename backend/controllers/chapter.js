const { PrismaClient } = require("@prisma/client");
const prisma = new PrismaClient();
const {
  getBoolean,
  getHTML,
  getAnswerFromAnsweredBy,
  getSingleUserAnswers,
  getAnswerFromUserAnswers,
} = require("./util");

const getChapters = async (payload) => {
  let isLoggedIn = true;
  if (!payload.user_id) {
    isLoggedIn = false;
  }
  console.log(isLoggedIn);
  // console.log(payload.user_id);
  try {
    const page = payload.page || 1;
    const perPage = payload.per_page || 10;
    const sortBy = payload.sort_by || "order";
    const sortOrder = payload.sort_type === "desc" ? "desc" : "asc";

    const chapters = await prisma.chapter.findMany({
      take: perPage,
      skip: (page - 1) * perPage,
      orderBy: {
        [sortBy]: sortOrder,
      },
      include: {
        lessons: true,
      },
    });

    if (isLoggedIn) {
      const favSet = new Set();

      const lesson_feedbacks = await prisma.feedback.findMany({
        where: {
          user_id: payload.user_id,
          lesson_id: {
            not: null,
          },
        },
      });

      for (const f of lesson_feedbacks) {
        if (f.is_starred) {
          favSet.add(f.lesson_id);
        }
      }

      for (let c of chapters) {
        for (let l of c.lessons) {
          l.is_starred = favSet.has(l.id);
          // console.log(l);
        }
      }
    } else {
      // for (let c of chapters) {
      //   for (let l of c.lessons) {
      //     l.is_starred = false;
      //     // console.log(l);
      //   }
      // }
    }

    return chapters;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

module.exports = { getChapters };
