'use client';

import { useState } from 'react';
import { FormEvent } from 'react';

interface OrderFormData {
  username: string;
  originLocation: string;
  destinationLocation: string;
  itemLength: number;
  itemWidth: number;
  itemHeight: number;
  itemWeight: number;
  pickupDeadline: string;
  specialInstructions: string;
  transportMode: string;
  priority: string;
}

export default function CreateOrderPage() {
  const [formData, setFormData] = useState<OrderFormData>({
    username: '',
    originLocation: '',
    destinationLocation: '',
    itemLength: 1,
    itemWidth: 1,
    itemHeight: 1,
    itemWeight: 1,
    pickupDeadline: '',
    specialInstructions: '',
    transportMode: 'none',
    priority: 'standard',
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log('Submitting:', formData);

    try {
      const response = await fetch('http://localhost:8000/api/orders', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...formData,
          // make sure your TS enum values match what FastAPI expects
        }),
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }

      const result = await response.json();
      alert(`Order submitted successfully! Order ID: ${result.orderId}`);
    } catch (error) {
      console.error('Submit error:', error);
      alert('Failed to submit order. Please try again.');
    }
  };

  return (
    <div className="">
      <h1 className="">
        Create Shipping Order
      </h1>
      
      <form onSubmit={handleSubmit} className="">
        {/* UserName */}
        <div>
          <label htmlFor="username" className="">
            Username *
          </label>
          <input
            type="text"
            id="username"
            name="username"
            value={formData.username}
            onChange={handleInputChange}
            required
            className=""
            placeholder="Enter username"
          />
        </div>

        {/* Locations */}
        <div className="">
          <div>
            <label htmlFor="originLocation" className="">
              Origin Location *
            </label>
            <input
              type="text"
              id="originLocation"
              name="originLocation"
              value={formData.originLocation}
              onChange={handleInputChange}
              required
              className=""
              placeholder="e.g., 123 Sesame St."
            />
          </div>
          <div>
            <label htmlFor="destinationLocation" className="">
              Destination Location *
            </label>
            <input
              type="text"
              id="destinationLocation"
              name="destinationLocation"
              value={formData.destinationLocation}
              onChange={handleInputChange}
              required
              className=""
              placeholder="e.g., 123 Sesame St."
            />
          </div>
        </div>

        {/* Items/Cargo Details */}
        <div>
          <div>
            <label htmlFor="itemLength" className="">
              Length *
            </label>
            <textarea
              id="itemLength"
              name="itemLength"
              rows={4}
              value={formData.itemLength}
              onChange={handleInputChange}
              required
              className=""
            />
          </div>
          <div>
            <label htmlFor="itemWidth" className="">
              Width *
            </label>
            <textarea
              id="itemWidth"
              name="itemWidth"
              rows={4}
              value={formData.itemWidth}
              onChange={handleInputChange}
              required
              className=""
            />
          </div>
          <div>
            <label htmlFor="itemHeight" className="">
              Height *
            </label>
            <textarea
              id="itemHeight"
              name="itemHeight"
              rows={4}
              value={formData.itemHeight}
              onChange={handleInputChange}
              required
              className=""
            />
          </div>
          <div>
            <label htmlFor="itemWeight" className="">
              Weight *
            </label>
            <textarea
              id="itemWeight"
              name="itemWeight"
              rows={4}
              value={formData.itemWeight}
              onChange={handleInputChange}
              required
              className=""
            />
          </div>
        </div>
        

        {/* Pickup Deadline */}
        <div>
          <label htmlFor="pickupDeadline" className="">
            Pickup Deadline *
          </label>
          <input
            type="datetime-local"
            id="pickupDeadline"
            name="pickupDeadline"
            value={formData.pickupDeadline}
            onChange={handleInputChange}
            required
            className=""
          />
        </div>

        {/* Special Instructions */}
        <div>
          <label htmlFor="specialInstructions" className="">
            Special Instructions
          </label>
          <textarea
            id="specialInstructions"
            name="specialInstructions"
            rows={3}
            value={formData.specialInstructions}
            onChange={handleInputChange}
            className=""
            placeholder="Any additional notes or requirements..."
          />
        </div>

        {/* Dropdowns */}
        <div className="">
          <div>
            <label htmlFor="transportMode" className="">
              Preferred Transport Mode *
            </label>
            <select
              id="transportMode"
              name="transportMode"
              value={formData.transportMode}
              onChange={handleInputChange}
              required
              className=""
            >
              <option value="none">None</option>
              <option value="truck">Truck</option>
              <option value="air">Air</option>
              <option value="rail">Rail</option>
              <option value="ocean">Boat</option>
            </select>
          </div>
          <div>
            <label htmlFor="priority" className="">
              Priority *
            </label>
            <select
              id="priority"
              name="priority"
              value={formData.priority}
              onChange={handleInputChange}
              required
              className=""
            >
              <option value="standard">Standard</option>
              <option value="express">Express</option>
            </select>
          </div>
        </div>

        {/* Submit Button */}
        <div className="pt-6">
          <button
            type="submit"
            className=""
          >
            Place Order
          </button>
        </div>
      </form>
    </div>
  );
}
