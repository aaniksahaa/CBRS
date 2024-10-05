import { api_base } from "./Constants"
import { getItem } from "./LocalStorage"

async function Fetch(url, stuff) {
  console.log('FETCH ->', url, JSON.stringify(stuff))
  const resp = await fetch(url, stuff)
  return resp
}

export function getAuthToken() {
  return getItem('authToken')
}

export async function fetchX(method, path, get, post) {
  console.log('fetchX ->', path, JSON.stringify(get))
  var url = `${api_base}/${path}/?`
  try {
    Object.keys(get).forEach(x => {
      url = url + x + '=' + get[x] + '&'
    })
  }
  catch { }
  const r = await Fetch(url, {
    method: method,
    mode: 'cors',
    headers: {
      'Authorization': getAuthToken(),
      'Access-Control-Allow-Origin': '*',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(post)
  })
  const j = await r.json()
  return j
}

export async function getX(path, filter) {
  console.log('getX ->', path, JSON.stringify(filter))
  var url = `${api_base}/${path}/?`
  try {
    Object.keys(filter).forEach(x => {
      url = url + x + '=' + filter[x] + '&'
    })
  }
  catch { }
  const r = await Fetch(url, {
    method: 'GET',
    headers: {
      'Authorization': getAuthToken()
    }
  })
  const j = await r.json()
  return j
}
export async function postX(path, filter, body) {
  console.log('postX ->', path, JSON.stringify(filter), JSON.stringify(body))
  var url = `${api_base}/${path}/?`
  try {
    Object.keys(filter).forEach(x => {
      url = url + x + '=' + filter[x] + '&'
    })
  }
  catch { }
  const r = await Fetch(url, {
    method: 'POST',
    mode: 'cors',
    headers: {
      'Authorization': getAuthToken(),
      'Access-Control-Allow-Origin': '*',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(body)
  })
  const j = await r.json()
  return j
}

export async function getSubjects() {
  const j = await getX('util/subjects', {})
  return j
}

export async function getChapters(subjectId) {
  const j = await getX(`util/chapters/${subjectId}`, {})
  return j
}

export async function getSlides(chapterId) {
  const j = await getX(`slide`, {"chapterId": chapterId})
  return j
}

export async function getSlide(slideId) {
  const j = await getX(`slide/${slideId}`, {})
  return j
}

export async function getLessons(filter) {
  const j = await getX('lesson', filter)
  return j
}

export async function getQuestion(id) {
  const j = await getX(`question/${id}`, {})
  return j
}

export async function getQuestions(filter) {
  const j = await getX(`question`, filter)
  return j
}

export async function createQuestion(data) {
  const j = await postX('question', {}, data)
  return j
}
export async function updateQuestion(data) {
  const j = await fetchX('PUT', 'question', {}, data)
  return j
}