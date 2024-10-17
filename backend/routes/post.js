const express = require("express");
const { validationResult } = require("express-validator");
const { createPost, getPosts } = require("../controllers/post");
const { getUserId } = require("../controllers/util");

const router = express.Router();

router.get("/", async (req, res, next) => {
  try {
    const posts = await getPosts(req.query);
    console.log(posts);
    res.json(posts);
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
    const post = await createPost(req.body);
    res.json(post);
  } catch (error) {
    console.log(error);
    next(error);
  }
});

module.exports = router;
