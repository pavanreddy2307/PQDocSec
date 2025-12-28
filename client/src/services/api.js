import { LOCAL_API, PEER_API } from "../config/api";

async function request(base, endpoint, options = {}) {
  const res = await fetch(`${base}${endpoint}`, options);
  return res.json();
}

export function localPost(endpoint, body, isForm = false) {
  return request(LOCAL_API, endpoint, {
    method: "POST",
    headers: isForm ? {} : { "Content-Type": "application/json" },
    body: isForm ? body : JSON.stringify(body),
  });
}

export function peerPost(endpoint, body, isForm = false) {
  if (!PEER_API) throw new Error("Peer not set");
  return request(PEER_API, endpoint, {
    method: "POST",
    headers: isForm ? {} : { "Content-Type": "application/json" },
    body: isForm ? body : JSON.stringify(body),
  });
}

export function localGet(endpoint) {
  return request(LOCAL_API, endpoint);
}

export function peerGet(endpoint) {
  if (!PEER_API) throw new Error("Peer not set");
  return request(PEER_API, endpoint);
}
