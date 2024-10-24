const { getChapters } = require("./controllers/chapter");
const generateStatistics = require("./controllers/stat");
const { getSingleUserProfile } = require("./controllers/user");

const f = async () => {
  const c = await generateStatistics();
  console.log(c);
};

// payload = {
//   user_id: "66ae41d47ce127c118b8f694",
// };

f();

const a = "abc";

console.log(!a);
