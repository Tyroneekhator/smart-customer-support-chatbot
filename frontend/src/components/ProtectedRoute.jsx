import { Navigate, useLocation } from "react-router-dom";
import { isAdminLoggedIn } from "../services/api";

function ProtectedRoute({ children }) {
  const location = useLocation();

  if (!isAdminLoggedIn()) {
    return (
      <Navigate
        to="/admin/login"
        replace
        state={{ from: location.pathname }}
      />
    );
  }

  return children;
}

export default ProtectedRoute;
