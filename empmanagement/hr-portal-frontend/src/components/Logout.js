import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

function Logout() {
  const navigate = useNavigate();

  useEffect(() => {
    const handleLogout = async () => {
      try {
        await axios.post('/api/auth/logout/');
        // Clear any local storage or state management data
        localStorage.removeItem('token');
        // Redirect to login page
        navigate('/login');
      } catch (error) {
        console.error('Logout failed:', error);
        // Even if the API call fails, we should still clear local data and redirect
        localStorage.removeItem('token');
        navigate('/login');
      }
    };

    handleLogout();
  }, [navigate]);

  return (
    <div className="text-center p-4">
      <p>Logging out...</p>
    </div>
  );
}

export default Logout; 