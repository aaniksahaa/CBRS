const { PrismaClient } = require("@prisma/client");
const prisma = new PrismaClient();
const {
  getBoolean,
  getHTML,
  getAnswerFromAnsweredBy,
  getSingleUserAnswers,
  getAnswerFromUserAnswers,
} = require("./util");

const getSingleLesson = async (payload) => {
  const include_all = payload.include_all
    ? getBoolean(payload.include_all)
    : true;

  console.log(include_all);

  try {
    const lesson = await prisma.lesson.findUnique({
      where: {
        id: payload.lesson_id,
      },
      include: {
        videos: include_all
          ? {
              include: {
                author: true,
              },
            }
          : false,
        geoviews: include_all,
        questions: include_all,
      },
    });

    if (include_all) {
      //Check if the user and question exist
      const existingUser = await prisma.user.findUnique({
        where: { id: payload.user_id },
      });

      // extracting all answers of this user
      const user_answers = await getSingleUserAnswers({
        user_id: payload.user_id,
      });

      //console.log(user_answers)

      // for each question, finding what answer this user gave to this question
      let answer_count = 0,
        correct_count = 0;
      for (let q of lesson.questions) {
        q.answer = getAnswerFromUserAnswers(user_answers, q.id);
        if (q.answer.attempted) {
          if (q.answer.chosen_option_index != -1) {
            answer_count++;
          }
          if (q.answer.chosen_option_index == q.correct_option_index) {
            correct_count++;
          }
        } else if (existingUser.role != "admin") {
          // console.log("blocking explanation access");
          q.correct_option_index = -420;
          q.explanation = "";
        }

        const feedbacks = await prisma.feedback.findMany({
          where: {
            user_id: payload.user_id,
          },
        });

        const question_feedbacks = feedbacks.filter(
          (feedback) => feedback.question_id !== null
        );
        const geoview_feedbacks = feedbacks.filter(
          (feedback) => feedback.geoview_id !== null
        );
        const video_feedbacks = feedbacks.filter(
          (feedback) => feedback.video_id !== null
        );

        // Convert the array to a map format
        const geoview_rating = geoview_feedbacks.reduce((map, feedback) => {
          map[feedback.geoview_id] = feedback.rating;
          return map;
        }, {});

        // Convert the array to a map format
        const video_rating = video_feedbacks.reduce((map, feedback) => {
          map[feedback.video_id] = feedback.rating;
          return map;
        }, {});

        // for each question find whether it was starred
        const favQuestionSet = new Set();

        for (const f of question_feedbacks) {
          if (f.is_starred) {
            favQuestionSet.add(f.question_id);
          }
        }

        for (let q of lesson.questions) {
          q.is_starred = favQuestionSet.has(q.id);
        }

        for (let g of lesson.geoviews) {
          g.rating = geoview_rating[g.id];
        }

        for (let v of lesson.videos) {
          v.rating = video_rating[v.id];
          v.author = {
            name: v.author.name,
            profile_picture_url: v.author.profile_picture_url,
          };
        }
      }
      lesson.question_count = lesson.questions.length;
      lesson.answer_count = answer_count;
      lesson.correct_count = correct_count;
    }
    console.log(lesson.videos);
    return lesson;
  } catch (err) {
    console.error(err);
    throw err;
  }
};

const getLessons = async (payload) => {
  const include_all = payload.include_all || true;
  //console.log(include_all)
  try {
    const page = payload.page || 1;
    const perPage = payload.per_page || 10;
    const sortBy = payload.sort_by || "id";
    const sortOrder = payload.sort_type === "desc" ? "desc" : "asc";
    // You can add additional filtering options based on your schema properties

    const lessons = await prisma.lesson.findMany({
      take: perPage,
      skip: (page - 1) * perPage,
      orderBy: {
        [sortBy]: sortOrder,
      },
      include: {
        videos: include_all,
        geoviews: include_all,
        questions: include_all,
      },
    });

    return lessons;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

const createLesson = async (payload) => {
  try {
    const lesson = await prisma.lesson.create({
      data: {
        title: payload.title,
        subtitle: payload.subtitle,
        description: payload.description,
        slide_url: payload.slide_url,
      },
      include: {
        videos: true,
        geoviews: true,
        questions: true,
      },
    });

    return lesson;
  } catch (err) {
    console.error(err);
    throw err;
  }
};

const updateLesson = async (payload) => {
  // payload must contain id and other attributes are optional
  // oly those which are being updated may be provided
  const { id, ...lessonData } = payload;
  try {
    const lesson = await prisma.lesson.update({
      where: {
        id: id,
      },
      data: {
        ...lessonData,
      },
      include: {
        videos: true,
        geoviews: true,
        questions: true,
      },
    });
    return lesson;
  } catch (err) {
    console.error(err);
    throw err;
  }
};

const deleteLesson = async (payload) => {
  const lessonId = payload.lesson_id;
  try {
    const lesson = await prisma.lesson.delete({
      where: {
        id: lessonId,
      },
    });
    return lesson;
  } catch (err) {
    console.error(err);
    throw err;
  }
};

module.exports = {
  getSingleLesson,
  getLessons,
  createLesson,
  updateLesson,
  deleteLesson,
};

/***
 * 
 * 
 * Create Lesson = POST
 * 
 * 
 * {
      "title": "Hadamard Gate 2",
      "subtitle": "The gate that is expert in creating equal superpositions",
      "description": "Hadamard gate has huge mathematical significance. And its often used in a lot of circuits.",
      "slide_url": "https://docs.google.com/presentation/d/e/2PACX-1vSB58fqnfgrqnpaLoHgJplsou3okvsiBJ_tLGkXGnaqvf53m64tQD0EbH9SrSr_fY0kPnjJUqsbZAAL"
   }
 */
