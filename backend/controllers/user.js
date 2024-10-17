const { PrismaClient } = require("@prisma/client");
const { getSingleLesson } = require("./lesson");
const { getSingleQuestion } = require("./question");
const prisma = new PrismaClient();

const getSingleUser = async (payload) => {
  try {
    const user = await prisma.user.findUnique({
      where: {
        id: payload.user_id,
      },
    });
    return user;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

const getSingleUserByUsername = async (payload) => {
  try {
    const user = await prisma.user.findUnique({
      where: {
        username: payload.username,
      },
    });
    return user;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

async function getAnswersFromUser(user_id) {
  const answers = await prisma.answer.findMany({
    where: {
      user_id: user_id,
    },
    include: {
      question: true, // Include the related question
    },
  });

  return answers;
}

async function getCorrectAnswers(answers) {
  // Filter out correct answers
  const correctAnswers = answers.filter(
    (answer) =>
      answer.chosen_option_index === answer.question.correct_option_index
  );

  return correctAnswers;
}

const getSingleUserProfile = async (payload) => {
  try {
    const user = await prisma.user.findUnique({
      where: {
        id: payload.user_id,
      },
    });

    const question_count = await prisma.question.count();
    const answers = await getAnswersFromUser(payload.user_id);
    const answer_count = answers.length;
    const correctAnswers = await getCorrectAnswers(answers);
    const correct_count = correctAnswers.length;

    const feedbacks = await prisma.feedback.findMany({
      where: {
        user_id: payload.user_id,
      },
    });

    const favorites = feedbacks.filter((feedback) => feedback.is_starred);

    const favorite_lesson_ids = favorites
      .filter((feedback) => feedback.lesson_id !== null)
      .map((feedback) => feedback.lesson_id);

    const favorite_question_ids = favorites
      .filter((feedback) => feedback.question_id !== null)
      .map((feedback) => feedback.question_id);

    let favorite_lessons = [];

    for (let id of favorite_lesson_ids) {
      favorite_lessons.push(
        await getSingleLesson({ lesson_id: id, include_all: "false" })
      );
    }

    let favorite_questions = [];

    for (let id of favorite_question_ids) {
      favorite_questions.push(await getSingleQuestion({ question_id: id }));
    }

    const profile = {
      ...user,
      question_count: question_count,
      answer_count: answer_count,
      correct_count: correct_count,
      favorites: {
        lessons: favorite_lessons,
        questions: favorite_questions,
      },
    };

    // console.log(profile);

    return profile;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

const getUsers = async (payload) => {
  const page = payload.page || 1;
  const perPage = payload.per_page || 10;
  const sortBy = payload.orderby || "username";
  const sortOrder = payload.ordertype === "desc" ? "desc" : "asc";

  try {
    const users = await prisma.user.findMany({
      take: perPage,
      skip: (page - 1) * perPage,
      orderBy: {
        [sortBy]: sortOrder,
      },
    });

    return users;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

const createUser = async (payload) => {
  try {
    const user = await prisma.user.create({
      data: {
        username: payload.username,
        password: payload.password,
        role: payload.role || "student",
        name: payload.name,
        bio: payload.bio || "",
        country: payload.country || "Bangladesh",
        city: payload.city || "",
        email: payload.email,
        google_uid: payload.google_uid,
        date_of_birth: payload.date_of_birth
          ? new Date(payload.date_of_birth)
          : null,
        profile_picture_url: payload.profile_picture_url || "dummy.jpg",
        institution: payload.institution || "",
      },
    });

    const response = {
      success: true,
      user: user,
    };

    return response;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

const updateUser = async (payload) => {
  console.log(payload);
  try {
    const user = await prisma.user.update({
      where: {
        id: payload.user_id,
      },
      data: {
        username: payload.username,
        password: payload.password,
        role: payload.role,
        name: payload.name,
        bio: payload.bio,
        country: payload.country,
        city: payload.city,
        email: payload.email,
        date_of_birth: new Date(payload.date_of_birth),
        profile_picture_url: payload.profile_picture_url,
        institution: payload.institution,
        updated_at: new Date(),
      },
    });
    return user;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

const deleteUser = async (payload) => {
  try {
    const user = await prisma.user.update({
      where: {
        id: payload.user_id,
      },
      data: {
        deleted_at: new Date(),
      },
    });
    return user;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

const deleteUserPermanent = async (payload) => {
  try {
    const user = await prisma.user.delete({
      where: {
        id: payload.user_id,
      },
    });
    return user;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

module.exports = {
  getSingleUser,
  getSingleUserByUsername,
  getSingleUserProfile,
  getUsers,
  createUser,
  updateUser,
  deleteUser,
  deleteUserPermanent,
};

/**  
 * Creating User - POST
 * 
 * {
        "username": "aaniksahaa",
        "password": "abc",
        "name": "Anik Saha",
        "email": "a@gmail.com",
        "date_of_birth": "2002-09-17",
        "profile_picture_url": "https://example.com/profile.jpg",
        "institution": "BUET",
        "bio": "Hello",
        "country": "Bangladesh",
        "city": "Dhaka",
        "role": "student"
    }

    Update User - PUT

 * {
        "user_id": "6505c87e7a524b867ddd8f83",
        "username": "aaniksahaa2",
        "password": "abc",
        "name": "Anik Saha",
        "email": "a@gmail.com",
        "date_of_birth": "2002-09-17",
        "profile_picture_url": "https://example.com/profile.jpg",
        "institution": "BUET",
        "bio": "Hello",
        "country": "Bangladesh",
        "city": "Dhaka",
        "role": "student"
    }

 * **/
