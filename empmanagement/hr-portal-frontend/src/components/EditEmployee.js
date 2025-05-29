import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';

function EditEmployee() {
  const { id } = useParams();
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
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const fetchEmployee = async () => {
      try {
        const response = await axios.get(`/api/employees/${id}/`);
        setFormData(response.data);
        setLoading(false);
      } catch (err) {
        setError('Failed to fetch employee details');
        setLoading(false);
      }
    };

    fetchEmployee();
  }, [id]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');

    try {
      await axios.put(`/api/employees/${id}/`, formData);
      navigate(`/employees/${id}`);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to update employee');
      setSaving(false);
    }
  };

  if (loading) return <div className="text-center p-4">Loading...</div>;
  if (error) return <div className="alert alert-error">{error}</div>;

  return (
    <div className="edit-employee">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Edit Employee</h1>
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
              onClick={() => navigate(`/employees/${id}`)}
              className="btn btn-secondary"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={saving}
            >
              {saving ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default EditEmployee; 