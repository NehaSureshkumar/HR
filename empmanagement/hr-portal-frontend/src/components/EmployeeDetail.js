import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import axios from 'axios';

function EmployeeDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [employee, setEmployee] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchEmployee = async () => {
      try {
        const response = await axios.get(`/api/employees/${id}/`);
        setEmployee(response.data);
        setLoading(false);
      } catch (err) {
        setError('Failed to fetch employee details');
        setLoading(false);
      }
    };

    fetchEmployee();
  }, [id]);

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this employee?')) {
      try {
        await axios.delete(`/api/employees/${id}/`);
        navigate('/employees');
      } catch (err) {
        setError('Failed to delete employee');
      }
    }
  };

  if (loading) return <div className="text-center p-4">Loading...</div>;
  if (error) return <div className="alert alert-error">{error}</div>;
  if (!employee) return <div className="alert alert-error">Employee not found</div>;

  return (
    <div className="employee-detail">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Employee Details</h1>
        <div className="flex space-x-2">
          <Link to={`/employees/${id}/edit`} className="btn btn-primary">
            Edit Employee
          </Link>
          <button onClick={handleDelete} className="btn btn-secondary text-red-600">
            Delete Employee
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Personal Information</h2>
          <div className="space-y-4">
            <div>
              <label className="font-medium">Full Name</label>
              <p>{employee.name}</p>
            </div>
            <div>
              <label className="font-medium">Email</label>
              <p>{employee.email}</p>
            </div>
            <div>
              <label className="font-medium">Phone</label>
              <p>{employee.phone}</p>
            </div>
            <div>
              <label className="font-medium">Address</label>
              <p>{employee.address}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Employment Information</h2>
          <div className="space-y-4">
            <div>
              <label className="font-medium">Position</label>
              <p>{employee.position}</p>
            </div>
            <div>
              <label className="font-medium">Department</label>
              <p>{employee.department}</p>
            </div>
            <div>
              <label className="font-medium">Join Date</label>
              <p>{new Date(employee.join_date).toLocaleDateString()}</p>
            </div>
            <div>
              <label className="font-medium">Status</label>
              <p className={`inline-block px-2 py-1 rounded-full text-sm ${
                employee.status === 'Active' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
              }`}>
                {employee.status}
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Documents</h2>
          <div className="space-y-4">
            {employee.documents?.map(doc => (
              <div key={doc.id} className="flex justify-between items-center">
                <span>{doc.name}</span>
                <a
                  href={doc.file_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn btn-secondary btn-sm"
                >
                  View
                </a>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Recent Activities</h2>
          <div className="space-y-4">
            {employee.activities?.map(activity => (
              <div key={activity.id} className="flex justify-between items-center">
                <span>{activity.description}</span>
                <span className="text-sm text-gray-500">
                  {new Date(activity.timestamp).toLocaleDateString()}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default EmployeeDetail; 