const express = require("express");
const { validationResult } = require("express-validator");
const { createFeedback, getFeedbacks } = require("../controllers/feedback");
const { getUserId } = require("../controllers/util");

const router = express.Router();

router.get("/", async (req, res, next) => {
  try {
    const feedbacks = await getFeedbacks(req.query);
    console.log(feedbacks);
    res.json(feedbacks);
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
    req.body.user_id = getUserId(req);
    const feedback = await createFeedback(req.body);
    res.json(feedback);
  } catch (error) {
    console.log(error);
    next(error);
  }
});

module.exports = router;
