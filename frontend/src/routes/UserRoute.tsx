import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";

export const UserRoute = () => {
  const { user } = useAuth();
  return user?.roleName === "user" ? <Outlet /> : <Navigate to="/unauthorized" replace />;
};
