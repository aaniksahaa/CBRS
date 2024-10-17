const express = require("express");
const { validationResult } = require("express-validator");
const {
  getSingleUser,
  getUsers,
  createUser,
  updateUser,
  deleteUser,
  deleteUserPermanent,
  getSingleUserProfile,
} = require("../controllers/user");
const { getUserId } = require("../controllers/util");

const router = express.Router();

router.get("/:user_id", async (req, res, next) => {
  try {
    const user = await getSingleUser(req.params);
    // console.log(user);
    res.json(user);
  } catch (err) {
    console.error(err);
    next(err);
  }
});

router.get("/:user_id/profile", async (req, res, next) => {
  try {
    const profile = await getSingleUserProfile(req.params);
    // console.log(profile);
    res.json(profile);
  } catch (err) {
    console.error(err);
    next(err);
  }
});

router.get("/", async (req, res, next) => {
  try {
    const users = await getUsers(req.query);
    // console.log(users);
    res.json(users);
  } catch (err) {
    console.error(err);
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
    const user = await createUser(req.body);
    res.json(user);
  } catch (error) {
    console.error(error);
    next(error);
  }
});

router.put("/", async (req, res, next) => {
  const result = validationResult(req);
  if (result.isEmpty() === false) {
    return res.send({ errors: result.array() });
  }
  console.log(req.body);
  req.body.user_id = getUserId(req);
  try {
    const user = await updateUser(req.body);
    res.json(user);
  } catch (error) {
    console.error(error);
    next(error);
  }
});

router.delete("/:user_id", async (req, res, next) => {
  const result = validationResult(req);
  if (result.isEmpty() === false) {
    return res.send({ errors: result.array() });
  }
  try {
    const user = await deleteUser(req.params);
    res.json(user);
  } catch (error) {
    console.error(error);
    next(error);
  }
});

router.delete("/:user_id/danger", async (req, res, next) => {
  const result = validationResult(req);
  if (result.isEmpty() === false) {
    return res.send({ errors: result.array() });
  }
  try {
    const user = await deleteUserPermanent(req.params);
    res.json(user);
  } catch (error) {
    console.error(error);
    next(error);
  }
});

module.exports = router;
