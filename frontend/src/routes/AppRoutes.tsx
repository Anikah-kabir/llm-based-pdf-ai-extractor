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
import PDFListPage from "@/pages/PDFListPage";
import PDFDetails from "@/pages/PDFDetails";
import ChunkSummary from "@/pages/ChunkDetailsPage";
import PromptEditor from "@/components/PromptEditor";

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
            <Route 
              path="/pdfs" 
              element={
                <Layout>
                  <PDFListPage />
                </Layout>
              } 
            />
            <Route 
              path="/pdfs/:id"
              element={
                <Layout>
                  <PDFDetails  />
                </Layout>
              } 
            />
            <Route 
              path="/pdfs/:id/chunks"
              element={
                <Layout>
                  <ChunkSummary  />
                </Layout>
              } 
            />
            <Route 
              path="/prompt-engineer"
              element={
                <Layout>
                  <PromptEditor  />
                </Layout>
              } 
            />
        </Route>
      </Routes>
  );
}
