const express = require("express");
const { validationResult } = require("express-validator");
const router = express.Router();
const { getUserId } = require("../controllers/util");
const { createVideo, updateVideo } = require("../controllers/video");

router.post("/", async (req, res, next) => {
  const result = validationResult(req);
  console.log(req.body);
  if (result.isEmpty() === false) {
    return res.send({ errors: result.array() });
  }
  try {
    req.body.user_id = getUserId(req);
    const video = await createVideo(req.body);
    res.json(video);
  } catch (error) {
    console.log(error);
    next(error);
  }
});

router.put("/", async (req, res, next) => {
  const result = validationResult(req);
  console.log(req.body);
  if (result.isEmpty() === false) {
    return res.send({ errors: result.array() });
  }
  try {
    // req.body.user_id = getUserId(req);
    const video = await updateVideo(req.body);
    res.json(video);
  } catch (error) {
    console.log(error);
    next(error);
  }
});

module.exports = router;
