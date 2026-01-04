export const LOCAL_API =
  import.meta.env.VITE_LOCAL_API || "http://localhost:5000";

// Peer API will be discovered dynamically
export let PEER_API = null;

export function setPeerApi(ip, port = 5050) {
  PEER_API = `http://${ip}:${port}`;
}
