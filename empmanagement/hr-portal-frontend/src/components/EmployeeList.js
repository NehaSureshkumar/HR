import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';

function EmployeeList() {
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchEmployees = async () => {
      try {
        const response = await axios.get('/api/employees/');
        setEmployees(response.data);
        setLoading(false);
      } catch (err) {
        setError('Failed to fetch employees');
        setLoading(false);
      }
    };

    fetchEmployees();
  }, []);

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this employee?')) {
      try {
        await axios.delete(`/api/employees/${id}/`);
        setEmployees(employees.filter(emp => emp.id !== id));
      } catch (err) {
        setError('Failed to delete employee');
      }
    }
  };

  if (loading) return <div className="text-center p-4">Loading...</div>;
  if (error) return <div className="alert alert-error">{error}</div>;

  return (
    <div className="employee-list">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Employee List</h1>
        <Link to="/employees/create" className="btn btn-primary">
          Add New Employee
        </Link>
      </div>

      <div className="card">
        <div className="overflow-x-auto">
          <table className="table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Position</th>
                <th>Department</th>
                <th>Email</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {employees.map(employee => (
                <tr key={employee.id}>
                  <td>
                    <Link to={`/employees/${employee.id}`} className="text-blue-600 hover:text-blue-800">
                      {employee.name}
                    </Link>
                  </td>
                  <td>{employee.position}</td>
                  <td>{employee.department}</td>
                  <td>{employee.email}</td>
                  <td>
                    <span className={`px-2 py-1 rounded-full text-sm ${
                      employee.status === 'Active' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {employee.status}
                    </span>
                  </td>
                  <td>
                    <div className="flex space-x-2">
                      <Link
                        to={`/employees/${employee.id}/edit`}
                        className="btn btn-secondary btn-sm"
                      >
                        Edit
                      </Link>
                      <button
                        onClick={() => handleDelete(employee.id)}
                        className="btn btn-secondary btn-sm text-red-600"
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default EmployeeList; 