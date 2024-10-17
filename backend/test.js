const { PrismaClient } = require("@prisma/client");
const { getSingleLesson, updateLesson } = require("./controllers/lesson");
const { createPost } = require("./controllers/post");
const prisma = new PrismaClient();

const f = async () => {
  const nonNull = await prisma.feedback.findMany({
    where: {
      user_id: "66ae41d47ce127c118b8f694",
      geoview_id: {
        not: null,
      },
    },
  });
  console.log(nonNull);
};

payload = {
  user_id: "6505c7cbe38e1b3d3569819e",
  text: "hello 2",
  parent_id: "66708f501a1f97fafd37b50b",
};

f();
