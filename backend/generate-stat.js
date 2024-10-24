const generateStatistics = require("./controllers/stat");

const f = async () => {
  const c = await generateStatistics();
  console.log(c);
};

f();

