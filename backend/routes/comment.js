const express = require("express");
const { validationResult } = require("express-validator");
const router = express.Router();
const { getUserId } = require("../controllers/util");
const { createComment } = require("../controllers/comment");

router.post("/", async (req, res, next) => {
  const result = validationResult(req);
  console.log(req.body);
  if (result.isEmpty() === false) {
    return res.send({ errors: result.array() });
  }
  try {
    req.body.user_id = getUserId(req);
    const comment = await createComment(req.body);
    res.json(comment);
  } catch (error) {
    console.log(error);
    next(error);
  }
});

module.exports = router;
