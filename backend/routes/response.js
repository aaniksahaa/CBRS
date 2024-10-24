// routes/response.js
const express = require("express");
const { validationResult } = require("express-validator");
const {
  getSingleResponse,
  getResponses,
  createResponse,
  updateResponse,
  deleteResponse,
  deleteResponsePermanent,
} = require("../controllers/response");

const router = express.Router();

router.get("/:response_id", async (req, res, next) => {
  try {
    const response = await getSingleResponse(req.params);
    res.json(response);
  } catch (err) {
    console.error(err);
    next(err);
  }
});

router.get("/", async (req, res, next) => {
  try {
    const responses = await getResponses(req.query);
    res.json(responses);
  } catch (err) {
    console.error(err);
    next(err);
  }
});

router.post("/", async (req, res, next) => {
  const result = validationResult(req);
  if (result.isEmpty() === false) {
    return res.send({ errors: result.array() });
  }
  try {
    const response = await createResponse(req.body);
    res.json(response);
  } catch (error) {
    console.error(error);
    next(error);
  }
});

router.put("/:response_id", async (req, res, next) => {
  const result = validationResult(req);
  if (result.isEmpty() === false) {
    return res.send({ errors: result.array() });
  }
  try {
    req.body.response_id = req.params.response_id;
    const response = await updateResponse(req.body);
    res.json(response);
  } catch (error) {
    console.error(error);
    next(error);
  }
});

router.delete("/:response_id", async (req, res, next) => {
  const result = validationResult(req);
  if (result.isEmpty() === false) {
    return res.send({ errors: result.array() });
  }
  try {
    const response = await deleteResponse(req.params);
    res.json(response);
  } catch (error) {
    console.error(error);
    next(error);
  }
});

router.delete("/:response_id/danger", async (req, res, next) => {
  const result = validationResult(req);
  if (result.isEmpty() === false) {
    return res.send({ errors: result.array() });
  }
  try {
    const response = await deleteResponsePermanent(req.params);
    res.json(response);
  } catch (error) {
    console.error(error);
    next(error);
  }
});

module.exports = router;