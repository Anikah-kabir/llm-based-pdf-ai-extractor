import { useAuth } from "@/context/AuthContext";
const Dashboard: React.FC = () => {
  const { user, logout } = useAuth();
  return (
    <div className="p-8">
      <h1 className="text-3xl font-semibold mb-4">Dashboard</h1>
      {user && (
        <div>
          <p>Welcome, ({user.username})</p>
          <p>Email: {user.email}</p>
          <button
            onClick={logout}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded"
          >
            Logout
          </button>
        </div>
      )}
    </div>
  );
};

export default Dashboard;