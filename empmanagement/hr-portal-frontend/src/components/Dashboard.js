import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';

function Dashboard() {
  const [stats, setStats] = useState({
    totalEmployees: 0,
    activeProjects: 0,
    pendingRequests: 0,
    recentActivities: []
  });

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const response = await axios.get('/api/dashboard/');
        setStats(response.data);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      }
    };

    fetchDashboardData();
  }, []);

  return (
    <div className="dashboard">
      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="card bg-blue-50">
          <h3 className="text-lg font-semibold text-blue-800">Total Employees</h3>
          <p className="text-3xl font-bold text-blue-600">{stats.totalEmployees}</p>
        </div>
        
        <div className="card bg-green-50">
          <h3 className="text-lg font-semibold text-green-800">Active Projects</h3>
          <p className="text-3xl font-bold text-green-600">{stats.activeProjects}</p>
        </div>
        
        <div className="card bg-yellow-50">
          <h3 className="text-lg font-semibold text-yellow-800">Pending Requests</h3>
          <p className="text-3xl font-bold text-yellow-600">{stats.pendingRequests}</p>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card mb-8">
        <h2 className="text-xl font-bold mb-4">Quick Actions</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Link to="/employees/create" className="btn btn-primary">
            Add Employee
          </Link>
          <Link to="/projects/create" className="btn btn-primary">
            Create Project
          </Link>
          <Link to="/attendance/mark" className="btn btn-primary">
            Mark Attendance
          </Link>
          <Link to="/documents/upload" className="btn btn-primary">
            Upload Document
          </Link>
        </div>
      </div>

      {/* Recent Activities */}
      <div className="card">
        <h2 className="text-xl font-bold mb-4">Recent Activities</h2>
        <div className="space-y-4">
          {stats.recentActivities.map((activity, index) => (
            <div key={index} className="flex items-center p-4 bg-gray-50 rounded-lg">
              <div className="flex-1">
                <p className="font-medium">{activity.description}</p>
                <p className="text-sm text-gray-500">{activity.timestamp}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default Dashboard; 