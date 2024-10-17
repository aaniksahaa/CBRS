const { getLessons } = require("./controllers/lesson");
const { getQuestions } = require("./controllers/question");
const fs = require('fs');
const { getUsers } = require("./controllers/user");

const getU = async () => {
    try {
      const u = await getUsers({});
      return u;
    }catch(err) {
      console.log(err)
    }
  }

const getL = async () => {
    try {
        const l = await getLessons({});
        return l;
    }catch(err) {
        console.log(err)
    }
}

const getQ = async () => {
    try {
      const q = await getQuestions({});
      return q;
    }catch(err) {
      console.log(err)
    }
  }

const write_json = (obj, filename) => {
    fs.writeFile(filename, JSON.stringify(obj, null, 2), 'utf8', (err) => {
        if (err) {
            console.error('Error writing JSON to file:', err);
            return;
        }
        console.log(`JSON object has been written to ${filename}`);
    });
}

const f = async() => {
    dir = 'backup_data/'
    const u = await getU()
    write_json(u, dir + 'users.json')
    const l = await getL()
    write_json(l, dir + 'lessons.json')
    const q = await getQ()
    write_json(q, dir + 'questions.json')
}

f()

