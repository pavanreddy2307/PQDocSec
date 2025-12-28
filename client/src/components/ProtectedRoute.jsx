import { Navigate } from "react-router-dom";

export default function ProtectedRoute({ role, allowed, children }) {
  if (!role) {
    return <Navigate to="/" replace />;
  }

  if (!allowed.includes(role)) {
    return <Navigate to="/" replace />;
  }

  return children;
}
