const { PrismaClient } = require("@prisma/client");

const prisma = new PrismaClient();

const getSingleQuestion = async (payload) => {
  const questionId = payload.question_id;
  try {
    const question = await prisma.question.findUnique({
      where: {
        id: questionId,
      },
      include: {
        // answered_by: true,
        // lesson: true,
        // author: true,
      },
    });
    return question;
  } catch (err) {
    console.error(err);
    throw err;
  }
};

const getAnswerFromUserQuestion = async (payload) => {
  try {
    const { user_id, question_id } = payload;
    let answer = {
      chosen_option_index: -1,
    };
    const answers = await prisma.answer.findMany({
      where: {
        user_id,
        question_id,
      },
    });
    if (answers.length > 0) {
      answer.chosen_option_index = answers[0].chosen_option_index;
    }
    return answer;
  } catch (err) {
    console.log(err);
  }
};

const getQuestions = async (payload) => {
  try {
    const page = payload.page || 1;
    const perPage = payload.per_page || 30;
    const sortBy = payload.sort_by || "id";
    const sortOrder = payload.sort_type === "desc" ? "desc" : "asc";

    const lesson_id = payload.lesson_id;
    const author_user_id = payload.author_user_id;
    const difficulty = payload.difficulty;

    let questions = await prisma.question.findMany({
      take: perPage,
      skip: (page - 1) * perPage,
      orderBy: {
        [sortBy]: sortOrder,
      },
      where: {
        ...(lesson_id && { lesson_id }),
        ...(author_user_id && { author_user_id }),
        ...(difficulty && { difficulty }),
      },
      include: {
        answered_by: true,
      },
    });

    //user_id = payload.user_id || '6505c7cbe38e1b3d3569819d';

    for (let q of questions) {
      required_answer = q.answered_by.find(
        (answer) => answer.user_id === payload.user_id
      );
      if (required_answer) {
        q.answer = {
          attempted: true,
          chosen_option_index: required_answer.chosen_option_index,
        };
      } else {
        q.answer = {
          attempted: false,
          chosen_option_index: -1,
        };
      }
    }

    return questions;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

const createQuestion = async (payload) => {
  try {
    const lesson = await prisma.lesson.findUnique({
      where: {
        id: payload.lesson_id,
      },
    });

    const author = await prisma.user.findUnique({
      where: {
        id: payload.author_user_id,
      },
    });

    if (!lesson || !author) {
      throw new Error("Invalid lesson_id or author_user_id");
    }

    const question = await prisma.question.create({
      data: {
        statement: payload.statement,
        statement_image_urls: payload.statement_image_urls || "",
        options: payload.options,
        option_image_urls: payload.option_image_urls || "",
        hints: payload.hints || "",
        correct_option_index: parseInt(payload.correct_option_index),
        difficulty: payload.difficulty.toLowerCase() || "medium",
        type: payload.type.toLowerCase() || "quiz",
        explanation: payload.explanation,
        explanation_image_urls: payload.explanation_image_urls || "",
        author: {
          connect: {
            id: payload.author_user_id,
          },
        },
        lesson: {
          connect: {
            id: payload.lesson_id,
          },
        },
      },
      include: {
        answered_by: true,
        lesson: true,
        author: true,
      },
    });

    return question;
  } catch (err) {
    console.error(err);
    throw err;
  }
};

const updateQuestion = async (payload) => {
  const question_id = payload.id;
  try {
    const question = await prisma.question.update({
      where: {
        id: question_id,
      },
      data: {
        statement: payload.statement,
        statement_image_urls: payload.statement_image_urls,
        options: payload.options,
        option_image_urls: payload.option_image_urls,
        hints: payload.hints,
        correct_option_index: parseInt(payload.correct_option_index),
        difficulty: payload.difficulty
          ? payload.difficulty.toLowerCase()
          : "medium",
        type: payload.type ? payload.type.toLowerCase() : "quiz",
        explanation: payload.explanation,
        explanation_image_urls: payload.explanation_image_urls,
      },
      include: {
        answered_by: true,
        lesson: true,
        author: true,
      },
    });
    return question;
  } catch (err) {
    console.error(err);
    throw err;
  }
};

const deleteQuestion = async (payload) => {
  const questionId = payload.question_id;
  try {
    const question = await prisma.question.delete({
      where: {
        id: questionId,
      },
    });
    return question;
  } catch (err) {
    console.error(err);
    throw err;
  }
};

module.exports = {
  getSingleQuestion,
  getQuestions,
  createQuestion,
  updateQuestion,
  deleteQuestion,
};

/*** **
 * Create Question POST 
 * 
 * {
        "lesson_id": "650228bba91bf52650ee94af",
        "statement": "What is the capital of France?",
        "statement_image_urls": "https://example.com/image1.jpg#https://example.com/image2.jpg",
        "options": "Berlin#Madrid#Paris#Rome",
        "option_image_urls": "null#null#null#null",
        "hints": "It starts with the letter 'P'#It's known as the 'City of Love'",
        "correct_option_index": 2,
        "difficulty": "medium",
        "explanation": "Paris is the capital city of France.",
        "explanation_image_urls": "https://example.com/explanation_image.jpg"
    }

 * 
 * 
 */
