const express = require("express");
const { validationResult } = require("express-validator");
const { createAnswer } = require("../controllers/answer"); // Assuming you have a lesson controller
const { getUserId } = require("../controllers/util");

const router = express.Router();

router.post("/", async (req, res, next) => {
  try {
    req.body.user_id = getUserId(req);
    const answer = await createAnswer(req.body);
    //console.log(answer);
    res.json(answer);
  } catch (err) {
    console.log(err);
    next(err);
  }
});

module.exports = router;
