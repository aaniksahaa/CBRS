const express = require("express");
const { validationResult } = require("express-validator");
const {
  getSingleQuestion,
  getQuestions,
  createQuestion,
  updateQuestion,
  deleteQuestion,
} = require("../controllers/question");
const { getUserId } = require("../controllers/util");

const router = express.Router();

router.get("/:question_id", async (req, res, next) => {
  try {
    const question = await getSingleQuestion(req.params);
    console.log(question);
    res.json(question);
  } catch (err) {
    console.log(err);
    next(err);
  }
});

router.get("/", async (req, res, next) => {
  try {
    req.query.user_id = getUserId(req);

    const questions = await getQuestions(req.query);
    console.log(questions);
    res.json(questions);
  } catch (err) {
    console.log(err);
    next(err);
  }
});

router.post("/", async (req, res, next) => {
  const result = validationResult(req);
  console.log(req.body);
  if (result.isEmpty() === false) {
    return res.send({ errors: result.array() });
  }
  try {
    req.body.author_user_id = req.user
      ? req.user.id
      : "6505c87e7a524b867ddd8f83";
    console.log("\n\n" + req.body.author_user_id + "\n\n");
    const question = await createQuestion(req.body);
    res.json(question);
  } catch (error) {
    console.log(error);
    next(error);
  }
});

router.put("/", async (req, res, next) => {
  const result = validationResult(req);
  if (result.isEmpty() === false) {
    return res.send({ errors: result.array() });
  }
  try {
    const question = await updateQuestion(req.body);
    res.json(question);
  } catch (error) {
    console.log(error);
    next(error);
  }
});

router.delete("/:question_id", async (req, res, next) => {
  const result = validationResult(req);
  if (result.isEmpty() === false) {
    return res.send({ errors: result.array() });
  }
  try {
    const question = await deleteQuestion(req.params);
    res.json(question);
  } catch (error) {
    console.log(error);
    next(error);
  }
});

module.exports = router;
