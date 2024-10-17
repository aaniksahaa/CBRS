const express = require("express");
const { validationResult } = require("express-validator");
const { getChapters } = require("../controllers/chapter");
const { getUserId } = require("../controllers/util");

const router = express.Router();

router.get("/", async (req, res, next) => {
  try {
    // req.query.user_id = getUserId(req);
    const chapters = await getChapters(req.query);
    //console.log(chapters);
    res.json(chapters);
  } catch (err) {
    console.log(err);
    next(err);
  }
});

module.exports = router;
