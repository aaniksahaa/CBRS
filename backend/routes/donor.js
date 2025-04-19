const express = require("express");
const { validationResult } = require("express-validator");
const {
  getSingleDonor,
  getDonors,
  createDonor,
  updateDonor,
  deleteDonor,
  deleteDonorPermanent,
  findProbableDonors,
} = require("../controllers/donor");

const router = express.Router();

router.get("/:donor_id", async (req, res, next) => {
  try {
    const donor = await getSingleDonor(req.params);
    res.json(donor);
  } catch (err) {
    console.error(err);
    next(err);
  }
});

router.get("/", async (req, res, next) => {
  try {
    const donors = await getDonors(req.query);
    res.json(donors);
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
    const donor = await createDonor(req.body);
    res.json(donor);
  } catch (error) {
    console.error(error);
    next(error);
  }
});

router.put("/:donor_id", async (req, res, next) => {
  const result = validationResult(req);
  if (result.isEmpty() === false) {
    return res.send({ errors: result.array() });
  }
  try {
    req.body.donor_id = req.params.donor_id;
    const donor = await updateDonor(req.body);
    res.json(donor);
  } catch (error) {
    console.error(error);
    next(error);
  }
});

router.delete("/:donor_id", async (req, res, next) => {
  const result = validationResult(req);
  if (result.isEmpty() === false) {
    return res.send({ errors: result.array() });
  }
  try {
    const donor = await deleteDonor(req.params);
    res.json(donor);
  } catch (error) {
    console.error(error);
    next(error);
  }
});

router.delete("/:donor_id/danger", async (req, res, next) => {
  const result = validationResult(req);
  if (result.isEmpty() === false) {
    return res.send({ errors: result.array() });
  }
  try {
    const donor = await deleteDonorPermanent(req.params);
    res.json(donor);
  } catch (error) {
    console.error(error);
    next(error);
  }
});

router.get("/match/:bloodrequest_id", async (req, res, next) => {
  try {
      const matchingDonors = await findProbableDonors({
          bloodrequest_id: req.params.bloodrequest_id
      });
      res.json(matchingDonors);
  } catch (err) {
      console.error(err);
      next(err);
  }
});

module.exports = router;