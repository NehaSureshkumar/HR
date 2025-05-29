import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

function CreateEmployee() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    address: '',
    position: '',
    department: '',
    join_date: '',
    status: 'Active'
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await axios.post('/api/employees/', formData);
      navigate('/employees');
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to create employee');
      setLoading(false);
    }
  };

  return (
    <div className="create-employee">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Create New Employee</h1>
      </div>

      <div className="card">
        <form onSubmit={handleSubmit} className="space-y-6">
          {error && <div className="alert alert-error">{error}</div>}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block font-medium mb-2">Full Name</label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
                className="form-input w-full"
                required
              />
            </div>

            <div>
              <label className="block font-medium mb-2">Email</label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                className="form-input w-full"
                required
              />
            </div>

            <div>
              <label className="block font-medium mb-2">Phone</label>
              <input
                type="tel"
                name="phone"
                value={formData.phone}
                onChange={handleChange}
                className="form-input w-full"
                required
              />
            </div>

            <div>
              <label className="block font-medium mb-2">Address</label>
              <input
                type="text"
                name="address"
                value={formData.address}
                onChange={handleChange}
                className="form-input w-full"
                required
              />
            </div>

            <div>
              <label className="block font-medium mb-2">Position</label>
              <input
                type="text"
                name="position"
                value={formData.position}
                onChange={handleChange}
                className="form-input w-full"
                required
              />
            </div>

            <div>
              <label className="block font-medium mb-2">Department</label>
              <input
                type="text"
                name="department"
                value={formData.department}
                onChange={handleChange}
                className="form-input w-full"
                required
              />
            </div>

            <div>
              <label className="block font-medium mb-2">Join Date</label>
              <input
                type="date"
                name="join_date"
                value={formData.join_date}
                onChange={handleChange}
                className="form-input w-full"
                required
              />
            </div>

            <div>
              <label className="block font-medium mb-2">Status</label>
              <select
                name="status"
                value={formData.status}
                onChange={handleChange}
                className="form-select w-full"
                required
              >
                <option value="Active">Active</option>
                <option value="Inactive">Inactive</option>
              </select>
            </div>
          </div>

          <div className="flex justify-end space-x-4">
            <button
              type="button"
              onClick={() => navigate('/employees')}
              className="btn btn-secondary"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading}
            >
              {loading ? 'Creating...' : 'Create Employee'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default CreateEmployee; 