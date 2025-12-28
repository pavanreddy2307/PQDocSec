import { useState } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";

import RoleSelector from "./components/RoleSelector";
import ProtectedRoute from "./components/ProtectedRoute";

import SenderDashboard from "./pages/SenderDashboard";
import ReceiverDashboard from "./pages/ReceiverDashboard";

export default function App() {
  const [role, setRole] = useState(null);

  return (
    <BrowserRouter>
      <Routes>
        {/* Public route */}
        <Route
          path="/"
          element={<RoleSelector onRoleSelected={setRole} />}
        />

        {/* Sender-only */}
        <Route
          path="/sender"
          element={
            <ProtectedRoute role={role} allowed={["SENDER"]}>
              <SenderDashboard />
            </ProtectedRoute>
          }
        />

        {/* Receiver-only */}
        <Route
          path="/receiver"
          element={
            <ProtectedRoute role={role} allowed={["RECEIVER"]}>
              <ReceiverDashboard />
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}
