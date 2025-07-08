const Unauthorized: React.FC = () => {
  return (
    <div className="text-center p-10">
      <h1 className="text-2xl font-bold text-red-600">403 - Unauthorized</h1>
      <p className="mt-4 text-gray-600">You do not have access to this page.</p>
    </div>
  );
};

export default Unauthorized;