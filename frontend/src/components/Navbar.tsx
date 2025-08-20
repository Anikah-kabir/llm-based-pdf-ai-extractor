import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Navbar: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="bg-blue-600 text-white px-6 py-4 shadow-md flex justify-between items-center">
      {user ? (
      <Link to="/dashboard" className="text-xl font-bold">
        LLM PDF Extractor Dashboard
      </Link>
       ) : (
      <Link to="/" className="text-xl font-bold">
        LLM PDF
      </Link>
      )}
      <div className="space-x-4 flex items-center">
        {user && (
          <>
            <Link to="/upload-pdf" className="hover:underline">
              Upload PDF
            </Link>
            <Link to="/prompt-engineer" style={{ marginLeft: "20px" }}>Prompt Engineering</Link>
            <Link to="/pdfs" style={{ marginLeft: "20px" }}>All Pdfs</Link>
          </>
        )}
        {user ? (
          <>
            <span className="mr-2">
              Hi, {user.username}
            </span>
            <button
              onClick={handleLogout}
              className="bg-red-500 hover:bg-red-600 px-3 py-1 rounded"
            >
              Logout
            </button>
          </>
        ) : (
          <>
            <Link to="/login" className="hover:underline">
              Login
            </Link>
            <Link to="/register" className="hover:underline">
              Register
            </Link>
          </>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
