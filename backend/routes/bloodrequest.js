const express = require("express");
const { validationResult } = require("express-validator");
const {
  getSingleBloodrequest,
  getBloodrequests,
  createBloodrequest,
  updateBloodrequest,
  deleteBloodrequest,
  deleteBloodrequestPermanent,
} = require("../controllers/bloodrequest");

const router = express.Router();

router.get("/:bloodrequest_id", async (req, res, next) => {
  try {
    const bloodrequest = await getSingleBloodrequest(req.params);
    res.json(bloodrequest);
  } catch (err) {
    console.error(err);
    next(err);
  }
});

router.get("/", async (req, res, next) => {
  try {
    const bloodrequests = await getBloodrequests(req.query);
    res.json(bloodrequests);
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
    const bloodrequest = await createBloodrequest(req.body);
    res.json(bloodrequest);
  } catch (error) {
    console.error(error);
    next(error);
  }
});

router.put("/:bloodrequest_id", async (req, res, next) => {
  const result = validationResult(req);
  if (result.isEmpty() === false) {
    return res.send({ errors: result.array() });
  }
  try {
    req.body.bloodrequest_id = req.params.bloodrequest_id;
    const bloodrequest = await updateBloodrequest(req.body);
    res.json(bloodrequest);
  } catch (error) {
    console.error(error);
    next(error);
  }
});

router.delete("/:bloodrequest_id", async (req, res, next) => {
  const result = validationResult(req);
  if (result.isEmpty() === false) {
    return res.send({ errors: result.array() });
  }
  try {
    const bloodrequest = await deleteBloodrequest(req.params);
    res.json(bloodrequest);
  } catch (error) {
    console.error(error);
    next(error);
  }
});

router.delete("/:bloodrequest_id/danger", async (req, res, next) => {
  const result = validationResult(req);
  if (result.isEmpty() === false) {
    return res.send({ errors: result.array() });
  }
  try {
    const bloodrequest = await deleteBloodrequestPermanent(req.params);
    res.json(bloodrequest);
  } catch (error) {
    console.error(error);
    next(error);
  }
});

module.exports = router;