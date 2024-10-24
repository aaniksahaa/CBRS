// routes/notification.js
const express = require("express");
const { validationResult } = require("express-validator");
const {
  getSingleNotification,
  getNotifications,
  createNotification,
  updateNotification,
  deleteNotification,
  deleteNotificationPermanent,
} = require("../controllers/notification");

const router = express.Router();

router.get("/:notification_id", async (req, res, next) => {
  try {
    const notification = await getSingleNotification(req.params);
    res.json(notification);
  } catch (err) {
    console.error(err);
    next(err);
  }
});

router.get("/", async (req, res, next) => {
  try {
    const notifications = await getNotifications(req.query);
    res.json(notifications);
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
    const notification = await createNotification(req.body);
    res.json(notification);
  } catch (error) {
    console.error(error);
    next(error);
  }
});

router.put("/:notification_id", async (req, res, next) => {
  const result = validationResult(req);
  if (result.isEmpty() === false) {
    return res.send({ errors: result.array() });
  }
  try {
    req.body.notification_id = req.params.notification_id;
    const notification = await updateNotification(req.body);
    res.json(notification);
  } catch (error) {
    console.error(error);
    next(error);
  }
});

router.delete("/:notification_id", async (req, res, next) => {
  const result = validationResult(req);
  if (result.isEmpty() === false) {
    return res.send({ errors: result.array() });
  }
  try {
    const notification = await deleteNotification(req.params);
    res.json(notification);
  } catch (error) {
    console.error(error);
    next(error);
  }
});

router.delete("/:notification_id/danger", async (req, res, next) => {
  const result = validationResult(req);
  if (result.isEmpty() === false) {
    return res.send({ errors: result.array() });
  }
  try {
    const notification = await deleteNotificationPermanent(req.params);
    res.json(notification);
  } catch (error) {
    console.error(error);
    next(error);
  }
});

module.exports = router;