const { PrismaClient } = require("@prisma/client");
const prisma = new PrismaClient();
const { default: axios } = require("axios");

const getBoolean = (x) => {
  return x == true || x == "true" ? true : false;
};

const getHTML = async (url) => {
  try {
    const response = await axios.get(url);
    return response.data;
  } catch (error) {
    console.error("Error fetching HTML:", error.message);
    return "";
    // throw error; // Re-throw the error to be handled by the caller if needed
  }
};

const getUserId = (req) => {
  return req.user ? req.user.id : null;
};

const getAnswerFromAnsweredBy = (answered_by, user_id) => {
  let answer = {};
  required_answer = answered_by.find((answer) => answer.user_id === user_id);
  if (required_answer) {
    answer = {
      attempted: true,
      chosen_option_index: required_answer.chosen_option_index,
    };
  } else {
    answer = {
      attempted: false,
      chosen_option_index: -1,
    };
  }
  return answer;
};

const getSingleUserAnswers = async (payload) => {
  try {
    const user = await prisma.user.findUnique({
      where: {
        id: payload.user_id,
      },
      include: {
        answered_questions: true,
      },
    });
    return user && user.answered_questions ? user.answered_questions : null;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

const getAnswerFromUserAnswers = (user_answers, question_id) => {
  let answer = {};
  required_answer = user_answers.find(
    (answer) => answer.question_id === question_id
  );
  if (required_answer) {
    answer = {
      attempted: true,
      chosen_option_index: required_answer.chosen_option_index,
    };
  } else {
    answer = {
      attempted: false,
      chosen_option_index: -1,
    };
  }
  return answer;
};

module.exports = {
  getBoolean,
  getHTML,
  getUserId,
  getAnswerFromAnsweredBy,
  getSingleUserAnswers,
  getAnswerFromUserAnswers,
};
