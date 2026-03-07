'use client';

import { useState } from 'react';
import { FormEvent } from 'react';

interface OrderFormData {
  customerName: string;
  originLocation: string;
  destinationLocation: string;
  itemsDetails: string;
  pickupDeadline: string;
  specialInstructions: string;
  transportMode: string;
  priority: string;
}

export default function OrderPage() {
  const [formData, setFormData] = useState<OrderFormData>({
    customerName: '',
    originLocation: '',
    destinationLocation: '',
    itemsDetails: '',
    pickupDeadline: '',
    specialInstructions: '',
    transportMode: 'truck',
    priority: 'standard',
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    console.log('Order submitted:', formData);
    // API call, etc.
    alert('Order submitted successfully!');
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-2xl mx-auto">
        <div className="bg-white shadow-xl rounded-lg p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-8 text-center">
            Create Shipping Order
          </h1>
          
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Customer Name */}
            <div>
              <label htmlFor="customerName" className="block text-sm font-medium text-gray-700 mb-2">
                Customer Name *
              </label>
              <input
                type="text"
                id="customerName"
                name="customerName"
                value={formData.customerName}
                onChange={handleInputChange}
                required
                className="w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Enter customer name"
              />
            </div>

            {/* Locations */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label htmlFor="originLocation" className="block text-sm font-medium text-gray-700 mb-2">
                  Origin Location *
                </label>
                <input
                  type="text"
                  id="originLocation"
                  name="originLocation"
                  value={formData.originLocation}
                  onChange={handleInputChange}
                  required
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="e.g., Toronto, ON"
                />
              </div>
              <div>
                <label htmlFor="destinationLocation" className="block text-sm font-medium text-gray-700 mb-2">
                  Destination Location *
                </label>
                <input
                  type="text"
                  id="destinationLocation"
                  name="destinationLocation"
                  value={formData.destinationLocation}
                  onChange={handleInputChange}
                  required
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="e.g., Vancouver, BC"
                />
              </div>
            </div>

            {/* Items/Cargo Details */}
            <div>
              <label htmlFor="itemsDetails" className="block text-sm font-medium text-gray-700 mb-2">
                Items/Cargo Details *
              </label>
              <textarea
                id="itemsDetails"
                name="itemsDetails"
                rows={4}
                value={formData.itemsDetails}
                onChange={handleInputChange}
                required
                className="w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-vertical"
                placeholder="Describe items, weight, dimensions, special handling requirements..."
              />
            </div>

            {/* Pickup Deadline */}
            <div>
              <label htmlFor="pickupDeadline" className="block text-sm font-medium text-gray-700 mb-2">
                Pickup Deadline *
              </label>
              <input
                type="datetime-local"
                id="pickupDeadline"
                name="pickupDeadline"
                value={formData.pickupDeadline}
                onChange={handleInputChange}
                required
                className="w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            {/* Special Instructions */}
            <div>
              <label htmlFor="specialInstructions" className="block text-sm font-medium text-gray-700 mb-2">
                Special Instructions
              </label>
              <textarea
                id="specialInstructions"
                name="specialInstructions"
                rows={3}
                value={formData.specialInstructions}
                onChange={handleInputChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-vertical"
                placeholder="Any additional notes or requirements..."
              />
            </div>

            {/* Dropdowns */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label htmlFor="transportMode" className="block text-sm font-medium text-gray-700 mb-2">
                  Preferred Transport Mode *
                </label>
                <select
                  id="transportMode"
                  name="transportMode"
                  value={formData.transportMode}
                  onChange={handleInputChange}
                  required
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="truck">Truck</option>
                  <option value="air">Air</option>
                  <option value="rail">Rail</option>
                  <option value="ocean">Ocean</option>
                </select>
              </div>
              <div>
                <label htmlFor="priority" className="block text-sm font-medium text-gray-700 mb-2">
                  Priority *
                </label>
                <select
                  id="priority"
                  name="priority"
                  value={formData.priority}
                  onChange={handleInputChange}
                  required
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="standard">Standard</option>
                  <option value="urgent">Urgent</option>
                  <option value="rush">Rush</option>
                </select>
              </div>
            </div>

            {/* Submit Button */}
            <div className="pt-6">
              <button
                type="submit"
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-4 px-6 rounded-lg shadow-lg focus:outline-none focus:ring-4 focus:ring-blue-300 transition duration-200"
              >
                Place Order
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
