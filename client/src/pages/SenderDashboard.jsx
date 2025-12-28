import { useState } from "react";

// NOTE: Replace these with your actual imports:
import { localPost } from "../services/api";
import { setPeerApi } from "../config/api";



export default function SenderDashboard() {
  const [state, setState] = useState("INIT");
  const [receiver, setReceiver] = useState(null);
  const [error, setError] = useState(null);

  const discover = async () => {
    setState("SEARCHING");
    setError(null);
    
    try {
      const res = await localPost("/sender/discover");
      
      // Validate response before setting peer API
      if (!res.receiver_ip || !res.receiver_port) {
        throw new Error("Invalid receiver data: missing IP or port");
      }
      
      // Only set peer API if both values are valid
      setPeerApi(res.receiver_ip, res.receiver_port);
      console.log("Set peer API to:", res.receiver_ip, res.receiver_port);
      
      setReceiver(res);
      setState("FOUND");
    } catch (err) {
      console.error("Discovery failed:", err);
      setState("ERROR");
      setError(err.message || "No receiver found");
    }
  };

  const handshake = async () => {
    setState("HANDSHAKING");
    setError(null);
    
    try {
      // Call your actual handshake API here
      // const result = await peerPost("/handshake", { ... });
      
      // Simulating handshake for now
      setTimeout(() => setState("READY"), 1500);
    } catch (err) {
      console.error("Handshake failed:", err);
      setState("ERROR");
      setError("Handshake failed. Please try again.");
    }
  };

  const retry = () => {
    setError(null);
    setReceiver(null);
    setState("INIT");
  };

  return (
    <div className="min-h-screen bg-slate-900 text-white flex flex-col items-center justify-center">
      {/* Radar */}
      <div className="relative w-72 h-72 rounded-full bg-slate-800 border border-emerald-400 shadow-lg overflow-hidden">
        {/* Grid */}
        <div className="absolute inset-0 rounded-full border border-emerald-700 opacity-30" />

        {/* Pulsing rings */}
        {state === "SEARCHING" && (
          <>
            <div className="absolute inset-0 rounded-full border-2 border-emerald-500 animate-ping opacity-20" />
            <div className="absolute inset-6 rounded-full border border-emerald-500 opacity-30" />
            <div className="absolute inset-12 rounded-full border border-emerald-500 opacity-30" />
          </>
        )}

        {/* Sweep */}
        {state === "SEARCHING" && (
          <div className="absolute inset-0 origin-center animate-spin-slow">
            <div className="absolute top-1/2 left-1/2 w-1/2 h-1 bg-gradient-to-r from-emerald-400 to-transparent" />
          </div>
        )}

        {/* Receiver dot */}
        {(state === "FOUND" || state === "HANDSHAKING" || state === "READY") && (
          <button
            onClick={handshake}
            disabled={state === "HANDSHAKING" || state === "READY"}
            className="absolute top-[30%] left-[65%] flex flex-col items-center group"
          >
            {/* Avatar */}
            <div className="w-14 h-14 rounded-full bg-emerald-500 flex items-center justify-center shadow-lg group-hover:scale-105 transition">
              <span className="text-xl">👤</span>
            </div>

            {/* Name */}
            <span className="mt-2 text-sm text-emerald-300">
              {receiver?.name || "Receiver"}
            </span>
          </button>
        )}

        {/* Center */}
        <div className="absolute inset-1/2 w-3 h-3 bg-emerald-400 rounded-full -translate-x-1/2 -translate-y-1/2" />
      </div>

      {/* Status */}
      <div className="mt-8 text-center">
        {state === "INIT" && (
          <button
            onClick={discover}
            className="px-6 py-3 rounded-lg bg-emerald-600 hover:bg-emerald-500 font-semibold transition"
          >
            Start Scan
          </button>
        )}

        {state === "SEARCHING" && (
          <p className="text-emerald-400 tracking-wide">
            Scanning network for receivers…
          </p>
        )}

        {state === "FOUND" && (
          <p className="text-emerald-400 font-semibold">
            Receiver found: {receiver.receiver_ip}
          </p>
        )}

        {state === "HANDSHAKING" && (
          <p className="text-indigo-400 animate-pulse">
            Establishing secure handshake…
          </p>
        )}

        {state === "READY" && (
          <p className="text-green-400 font-bold text-lg">
            Secure channel established ✔
          </p>
        )}

        {state === "ERROR" && (
          <div className="space-y-4">
            <p className="text-red-400 font-semibold">
              ⚠ {error}
            </p>
            <button
              onClick={retry}
              className="px-6 py-3 rounded-lg bg-red-600 hover:bg-red-500 font-semibold transition"
            >
              Try Again
            </button>
          </div>
        )}
      </div>
    </div>
  );
}