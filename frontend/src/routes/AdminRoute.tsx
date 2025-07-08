import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";

export const AdminRoute = () => {
  const { user } = useAuth();
  return user?.roleName === "admin" ? <Outlet /> : <Navigate to="/unauthorized" replace />;
};
