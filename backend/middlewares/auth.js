const jwt = require("jsonwebtoken");

const isAuthorized = (req, res, next) => {
  const token = req.headers.authorization;
  // console.log(token)
  if (token) {
    jwt.verify(token, process.env.SECRET, (err, user) => {
      if (err) {
        console.log("Error while validating token");
        return res.sendStatus(403);
      } else {
        // console.log(user)
        req.user = user;
      }
      next();
    });
  } else {
    console.log("No token received");
    res.status(401).json({
      success: false,
      ERROR: true,
      AUTH_ERROR: true,
      status: 401,
      message: "unauthorized",
      stack: process.env.NODE_ENV === "development" ? err.stack : {},
    });
  }
};

module.exports = isAuthorized;
