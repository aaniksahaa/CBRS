const router = require("express").Router();
const { body, validationResult } = require("express-validator");
const { getTokenFromGoogleUid } = require("../controllers/auth");

router.post("/google/", [body("token").notEmpty()], async (req, res, next) => {
  console.log(req.body);
  const result = validationResult(req);
  if (result.isEmpty() === false) {
    return res.send({ errors: result.array() });
  }

  try {
    const auth_response = await getTokenFromGoogleUid(req.body);
    res.json(auth_response);
  } catch (err) {
    // console.log(err);
    next(err);
  }
});

module.exports = router;
