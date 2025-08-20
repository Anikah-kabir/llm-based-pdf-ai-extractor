import { useAuth } from "@/context/AuthContext";
import React, { useEffect, useState } from "react";
import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from "chart.js";
import { getChunks } from '@/api/pdfApi';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);


const Dashboard: React.FC = () => {
  const { user, logout } = useAuth();

  const [chartData, setChartData] = useState(null);

useEffect(() => {
  getChunks()
    .then((data) => {
      const labels = data.map((item) => item.filename); // typo fix: 'filenam' -> 'filename'
      const values = data.map((item) => item.chunk_count);

      setChartData({
        labels,
        datasets: [
          {
            label: "Chunk Count",
            data: values,
            backgroundColor: "rgba(75, 192, 192, 0.6)",
            borderColor: "rgba(75, 192, 192, 1)",
            borderWidth: 1
          }
        ]
      });
    })
    .catch((err) => console.error(err));
}, []);



  if (!chartData) return <p>Loading chart...</p>;

  return (
    <div className="p-8 bg-gray-50 min-h-screen">
    <h1 className="text-4xl font-bold mb-8 text-gray-800">Dashboard</h1>

    {user && (
      <div className="space-y-6">
        {/* User Info Card */}
        <div className="bg-white rounded-2xl shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-700 mb-4">User Info</h2>
          <p className="text-gray-600">👤 <span className="font-medium">{user.username}</span></p>
          <p className="text-gray-600">📧 {user.email}</p>

          <button
            onClick={logout}
            className="mt-4 px-5 py-2 rounded-xl bg-red-500 hover:bg-red-600 text-white font-medium transition-all"
          >
            Logout
          </button>
        </div>

        {/* Chart Card */}
        <div className="bg-white rounded-2xl shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-700 mb-6">
            PDF Chunk Count per Document
          </h2>
          <div className="w-full max-w-2xl mx-auto">
            <Bar
              data={chartData}
              options={{
                responsive: true,
                plugins: {
                  legend: { position: "top" },
                  title: {
                    display: true,
                    text: "PDF Chunk Distribution",
                    font: { size: 18 },
                  },
                },
              }}
            />
          </div>
        </div>
      </div>
    )}
    </div>
  );
};

export default Dashboard;