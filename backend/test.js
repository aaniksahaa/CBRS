const { PrismaClient } = require("@prisma/client");
const { getSingleLesson, updateLesson } = require("./controllers/lesson");
const { createPost } = require("./controllers/post");
const { findProbableDonors } = require("./controllers/donor");
const prisma = new PrismaClient();

const f = async (payload) => {
  const res = await findProbableDonors(payload);
  console.log(res);
};

payload = {
  bloodrequest_id: "671159b20d04598a1bb19bb3",
};

f(payload);
