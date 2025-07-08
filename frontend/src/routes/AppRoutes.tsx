import { Routes, Route } from "react-router-dom";
import { ProtectedRoute } from "@/routes/ProtectedRoute";
//import { AdminRoute } from "@/routes/AdminRoute";
//import { UserRoute } from "@/routes/UserRoute";

import Login from '@/pages/Login';
import Register from '@/pages/Register';
import Dashboard from '@/pages/Dashboard';
//import AdminDashboard from '../pages/AdminDashboard';
import NotFound from '@/pages/NotFound';
import Home from '@/pages/Home';
import Layout from '@/components/Layout';
import Unauthorized from "@/pages/Unauthorized";
import PdfUpload from "@/pages/PdfUpload";

export default function AppRoutes() {
  return (
    <Routes>
        {/* Public */}
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/unauthorized" element={<Unauthorized />} />
        <Route path="*" element={<NotFound />} />
        {/* Protected routes */}
        <Route element={<ProtectedRoute />}>
            <Route
              path="/dashboard"
              element={
                <Layout>
                  <Dashboard />
                </Layout>
              }
            />
            <Route 
              path="/upload-pdf" 
              element={
                <Layout>
                  <PdfUpload />
                </Layout>
              } 
            />
        </Route>
      </Routes>
  );
}
