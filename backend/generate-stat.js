const {generateDonorCSV, generateResponseStatCSV} = require("./controllers/stat");

const f = async () => {
  await generateDonorCSV();
  await generateResponseStatCSV();
};

f();

