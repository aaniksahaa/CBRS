import {
  api_base,
  AUTH_ERROR_CONFIG,
  AUTH_ERROR_MESSAGE,
  CACHE_TTL_MS,
  DEBUG,
  MAX_PING,
  NOT_RESPONDING_CONFIG,
  NOT_RESPONDING_MESSAGE,
  PING_INTERVAL,
  REQUEST_TIMEOUT,
  SERVER_ERROR_MESSAGE,
} from "./Config";
import { getItem } from "./LocalStorage";
import { toast } from "react-toastify";

// async function Fetch(url, stuff) {
//   // console.log("FETCH ->", url, JSON.stringify(stuff));
//   const resp = await fetch(url, stuff);
//   return resp;
// }

const fetchWithTimeout = async (
  url,
  options = {},
  timeout = REQUEST_TIMEOUT
) => {
  // Create a promise that rejects after the specified timeout
  const timeoutPromise = new Promise((_, reject) =>
    setTimeout(() => reject(new Error("Request timed out")), timeout)
  );

  // Fetch the resource and race it against the timeout promise
  const fetchPromise = fetch(url, options);

  // Use Promise.race to handle whichever promise settles first
  const response = await Promise.race([fetchPromise, timeoutPromise]);

  return response;
};

async function Fetch(url, stuff) {
  //console.log('FETCH ->', url, JSON.stringify(stuff))
  const resp = await fetchWithTimeout(url, stuff);
  // const resp = await fetch(url, stuff);
  return resp;
}

export function getAuthToken() {
  return getItem("authToken");
}

export async function fetchX(method, path, get, post) {
  //console.log('fetchX ->', path, JSON.stringify(get))
  var url = `${api_base}/${path}/?`;
  try {
    Object.keys(get).forEach((x) => {
      url = url + x + "=" + get[x] + "&";
    });
  } catch {}
  try {
    const r = await Fetch(url, {
      method: method,
      mode: "cors",
      headers: {
        Authorization: getAuthToken(),
        "Access-Control-Allow-Origin": "*",
        "Content-Type": "application/json",
      },
      body: JSON.stringify(post),
    });
    const j = await r.json();
    if (j.ERROR) {
      if (j.SERVER_ERROR) {
        toast.error(SERVER_ERROR_MESSAGE);
      } else if (j.AUTH_ERROR) {
        toast.error(AUTH_ERROR_MESSAGE, AUTH_ERROR_CONFIG);
      }
    }
    return j;
  } catch {
    console.log("\n\nServer did not respond\n\n");
    toast.warn(NOT_RESPONDING_MESSAGE, NOT_RESPONDING_CONFIG);
    const r = {
      success: false,
      ERROR: true,
      NOT_RESPONDING: true,
    };
    return r;
  }
}

export async function getX(path, filter) {
  // console.log("getX ->", path, JSON.stringify(filter));
  var url = `${api_base}/${path}/?`;
  try {
    Object.keys(filter).forEach((x) => {
      url = url + x + "=" + filter[x] + "&";
    });
  } catch {}
  try {
    const r = await Fetch(url, {
      method: "GET",
      headers: {
        Authorization: getAuthToken(),
      },
    });
    const j = await r.json();
    if (j.ERROR) {
      if (j.SERVER_ERROR) {
        toast.error(SERVER_ERROR_MESSAGE);
      } else if (j.AUTH_ERROR) {
        if (!path.includes("lesson")) {
          console.log("showing auth toast");
          toast.success(AUTH_ERROR_MESSAGE, AUTH_ERROR_CONFIG);
        }
      }
    }
    return j;
  } catch {
    if (!(path == "knock")) {
      console.log("\n\nServer did not respond\n\n");
      toast.warn(NOT_RESPONDING_MESSAGE, NOT_RESPONDING_CONFIG);
    }
    const r = {
      success: false,
      ERROR: true,
      NOT_RESPONDING: true,
    };
    return r;
  }
}
export async function postX(path, filter, body) {
  //console.log('postX ->', path, JSON.stringify(filter), JSON.stringify(body))
  var url = `${api_base}/${path}/?`;
  try {
    Object.keys(filter).forEach((x) => {
      url = url + x + "=" + filter[x] + "&";
    });
  } catch {}
  try {
    const r = await Fetch(url, {
      method: "POST",
      mode: "cors",
      headers: {
        Authorization: getAuthToken(),
        "Access-Control-Allow-Origin": "*",
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });
    const j = await r.json();
    if (j.ERROR) {
      if (j.SERVER_ERROR) {
        toast.error(SERVER_ERROR_MESSAGE);
      } else if (j.AUTH_ERROR) {
        toast.error(AUTH_ERROR_MESSAGE, AUTH_ERROR_CONFIG);
      }
    }
    return j;
  } catch {
    console.log("\n\nServer did not respond\n\n");
    toast.warn(NOT_RESPONDING_MESSAGE, NOT_RESPONDING_CONFIG);
    const r = {
      success: false,
      ERROR: true,
      NOT_RESPONDING: true,
    };
    return r;
  }
}

export async function putX(path, filter, body) {
  //console.log('postX ->', path, JSON.stringify(filter), JSON.stringify(body))
  var url = `${api_base}/${path}/?`;
  try {
    Object.keys(filter).forEach((x) => {
      url = url + x + "=" + filter[x] + "&";
    });
  } catch {}
  try {
    const r = await Fetch(url, {
      method: "PUT",
      mode: "cors",
      headers: {
        Authorization: getAuthToken(),
        "Access-Control-Allow-Origin": "*",
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });
    const j = await r.json();
    if (j.ERROR) {
      if (j.SERVER_ERROR) {
        toast.error(SERVER_ERROR_MESSAGE);
      } else if (j.AUTH_ERROR) {
        toast.error(AUTH_ERROR_MESSAGE, AUTH_ERROR_CONFIG);
      }
    }
    return j;
  } catch {
    console.log("\n\nServer did not respond\n\n");
    toast.warn(NOT_RESPONDING_MESSAGE, NOT_RESPONDING_CONFIG);
    const r = {
      success: false,
      ERROR: true,
      NOT_RESPONDING: true,
    };
    return r;
  }
}

export async function getKnock() {
  const j = await getX("knock", {});
  const alive = j.alive || false;
  if (DEBUG) {
    console.log(alive ? "Server is active" : "Trying to connect...");
  }
  return alive;
}

export async function getHeartbeat() {
  const j = await getX("heartbeat", {});
  const alive = j.alive || false;
  if (DEBUG) {
    console.log(alive ? "Server is active" : "Trying to connect...");
  }
  return alive;
}

export async function getSubjects() {
  const j = await getX("util/subjects", {});
  return j;
}

export async function getChapters(subjectId) {
  const j = await getX(`util/chapters/${subjectId}`, {});
  return j;
}

export async function getSlides(chapterId) {
  const j = await getX(`slide`, { chapterId: chapterId });
  return j;
}

export async function getSlide(slideId) {
  const j = await getX(`slide/${slideId}`, {});
  return j;
}

export async function getDonor(donorId) {
  const j = await getX(`donor/${donorId}`, {});
  return j;
}

export async function createDonor(data) {
  const j = await postX("donor", {}, data);
  return j;
}

export async function updateDonor(donorId, data) {
  const j = await fetchX("PUT", `donor/${donorId}`, {}, data);
  return j;
}

export async function getLessons(filter) {
  const j = await getX("lesson", filter);
  return j;
}

export async function getQuestion(id) {
  const j = await getX(`question/${id}`, {});
  return j;
}

export async function getQuestions(filter) {
  const j = await getX(`question`, filter);
  return j;
}

export async function createQuestion(data) {
  const j = await postX("question", {}, data);
  return j;
}
export async function updateQuestion(data) {
  const j = await fetchX("PUT", "question", {}, data);
  return j;
}
