import { FaEye, FaEyeSlash } from "react-icons/fa";

let api_base;

// const localhost_backend_url = 'http://192.168.229.36:3000'
const localhost_backend_url = "http://localhost:3000";
// const remote_backend_url = "https://qlearn.onrender.com";
const remote_backend_url = "https://delta-blood-bot-backend.onrender.com";

if (process.env.NODE_ENV === "development") {
  api_base = localhost_backend_url;

  // for remote backend from local
  // api_base = remote_backend_url;
} else {
  api_base = remote_backend_url;
}

function debug(...args) {
  if (process.env.NODE_ENV === "development") {
    console.log(...args);
  }
}

const primary_dark = "#800080";
const primary_light = "#FFE6FF";
const secondary_dark = "#005242";
const secondary_light = "#8AEAE7";
const tertiary_dark = "#55433B";
const tertiary_light = "#CCA290";

const unhide_icon = <FaEye />;
const hide_icon = <FaEyeSlash />;

const CACHE_TTL_MS = 3 * 86400 * 1000;

const REDIRECT_TIMEOUT = 600;
const REQUEST_TIMEOUT = 15000;
const MAX_PING = 5;
const PING_INTERVAL = 5000;

const NOT_RESPONDING_TOAST_DURATION = REQUEST_TIMEOUT + PING_INTERVAL;

const SERVER_ERROR_MESSAGE = "Sorry! Unexpected server error.";
const ADMIN_HASH_MARKER = "admin-200300";
const NOT_RESPONDING_MESSAGE = "Connnecting... Please wait...";
const AUTH_ERROR_MESSAGE = "Please login to perform this action.";

const SERVER_ERROR_CONFIG = { autoClose: 3000 };
const NOT_RESPONDING_CONFIG = { autoClose: NOT_RESPONDING_TOAST_DURATION };
const AUTH_ERROR_CONFIG = { autoClose: 1000 };

const DEBUG = process.env.NODE_ENV === "development";

export {
  debug,
  api_base,
  ADMIN_HASH_MARKER,
  CACHE_TTL_MS,
  REDIRECT_TIMEOUT,
  REQUEST_TIMEOUT,
  MAX_PING,
  PING_INTERVAL,
  SERVER_ERROR_MESSAGE,
  SERVER_ERROR_CONFIG,
  NOT_RESPONDING_MESSAGE,
  NOT_RESPONDING_CONFIG,
  NOT_RESPONDING_TOAST_DURATION,
  AUTH_ERROR_MESSAGE,
  AUTH_ERROR_CONFIG,
  primary_dark,
  primary_light,
  secondary_dark,
  secondary_light,
  tertiary_dark,
  tertiary_light,
  hide_icon,
  unhide_icon,
  DEBUG,
};
