const { PrismaClient } = require("@prisma/client");
const prisma = new PrismaClient();

const createAnswer = async (payload) => {
  try {
    const { user_id, question_id, chosen_option_index } = payload;

    // Check if the user and question exist
    const existingUser = await prisma.user.findUnique({
      where: { id: user_id },
    });

    const existingQuestion = await prisma.question.findUnique({
      where: { id: question_id },
    });

    if (!existingUser || !existingQuestion) {
      throw new Error("User or Question not found");
    }

    // Create the answer
    const createdAnswer = await prisma.answer.create({
      data: {
        user: { connect: { id: user_id } },
        question: { connect: { id: question_id } },
        chosen_option_index,
      },
    });

    const answerResponse = {
      success: true,
      correct_option_index: existingQuestion.correct_option_index,
      is_correct: chosen_option_index == existingQuestion.correct_option_index,
      explanation: existingQuestion.explanation,
    };

    //return createdAnswer;
    return answerResponse;
  } catch (err) {
    console.error("Error creating answer:", err);
    throw err;
  }
};

module.exports = { createAnswer };
