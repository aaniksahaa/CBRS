/// test 

const express = require("express");
const router = express.Router();
const morgan = require("morgan");
const cors = require("cors");
require("dotenv").config();

// Routes

const donorRouter = require("./routes/donor");
const bloodrequestRouter = require("./routes/bloodrequest");
// const notificationRouter = require("./routes/notification");

// Middleswares

const errorhandler = require("./middlewares/errorhandler");

// Declare and configure the app

const app = express();

app.use(morgan("dev"));
app.use(express.json());
app.use(
  cors({
    origin: "*",
    methods: "GET,POST,PUT,DELETE, PATCH",
    credentials: true,
    maxAge: 36000,
  })
);

// Link routes to routers, demo url = 'api/v1/demo?data=anik'

app.get("/knock", (req, res) => res.json({ alive: true }));
app.get("/heartbeat", (req, res) => res.json({ alive: true }));

app.use("/donor", donorRouter);
app.use("/bloodrequest", bloodrequestRouter);
// app.use("/notification", notificationRouter);

// Use errorhandler

app.use(errorhandler);

// Set up the connection

const port = process.env.PORT || 3000;
// const ip_address = process.env.IP_ADDRESS || "192.168.229.36";

app.listen(port, console.log(`Listening on port ${port}`));
// app.listen(port, ip_address, console.log(`Listening on port ${port}`));
