const express = require("express");
const { validationResult } = require("express-validator");
const {
  getSingleLesson,
  getLessons,
  createLesson,
  updateLesson,
  deleteLesson,
} = require("../controllers/lesson"); // Assuming you have a lesson controller
const { getUserId } = require("../controllers/util");

const router = express.Router();

router.get("/:lesson_id", async (req, res, next) => {
  try {
    req.params.user_id = getUserId(req);
    const lesson = await getSingleLesson({
      ...req.params,
      ...req.query,
    });
    //console.log(lesson);
    res.json(lesson);
  } catch (err) {
    console.log(err);
    next(err);
  }
});

router.get("/", async (req, res, next) => {
  try {
    const lessons = await getLessons(req.query);
    //console.log(lessons);
    res.json(lessons);
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
      ? req.user.user_id
      : "6505c87e7a524b867ddd8f83";
    const lesson = await createLesson(req.body);
    res.json(lesson);
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
    const lesson = await updateLesson(req.body);
    res.json(lesson);
  } catch (error) {
    console.log(error);
    next(error);
  }
});

router.delete("/:lesson_id", async (req, res, next) => {
  const result = validationResult(req);
  if (result.isEmpty() === false) {
    return res.send({ errors: result.array() });
  }
  try {
    const lesson = await deleteLesson(req.params);
    res.json(lesson);
  } catch (error) {
    console.log(error);
    next(error);
  }
});

module.exports = router;
