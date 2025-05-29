import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import './styles/App.css';

// Components
import Dashboard from './components/Dashboard';
import Login from './components/Login';
import Logout from './components/Logout';
import EmployeeList from './components/EmployeeList';
import EmployeeDetail from './components/EmployeeDetail';
import CreateEmployee from './components/CreateEmployee';
import EditEmployee from './components/EditEmployee';

function App() {
  return (
    <Router>
      <div className="app">
        {/* Navigation */}
        <nav className="bg-white shadow-lg">
          <div className="max-w-7xl mx-auto px-4">
            <div className="flex justify-between h-16">
              <div className="flex items-center">
                <img src="/images/logo.png" alt="Company Logo" className="h-10 mr-2" />
                <Link to="/" className="text-xl font-bold text-gray-800">
                  EMS
                </Link>
              </div>
              
              <div className="flex items-center">
                <Link to="/login" className="text-gray-600 hover:text-gray-900">Login</Link>
              </div>
            </div>
          </div>
        </nav>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/login" element={<Login />} />
            <Route path="/logout" element={<Logout />} />
            <Route path="/employees" element={<EmployeeList />} />
            <Route path="/employees/create" element={<CreateEmployee />} />
            <Route path="/employees/:id" element={<EmployeeDetail />} />
            <Route path="/employees/:id/edit" element={<EditEmployee />} />
          </Routes>
        </main>

        {/* Footer */}
        <footer className="bg-white shadow-lg mt-8">
          <div className="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8">
            <p className="text-center text-gray-500">
              © {new Date().getFullYear()} Employee Management System. All rights reserved.
            </p>
          </div>
        </footer>
      </div>
    </Router>
  );
}

export default App; 