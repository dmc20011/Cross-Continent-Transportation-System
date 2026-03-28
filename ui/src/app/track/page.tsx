"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";


type Order = {
  parentNumber: string;
  orderNumber: string;
  orderDate: string;
  orderLastUpdate: string;
  startLocation: string;
  currentLocation: string;
  targetLocation: string;
  distkm: number;
  transportationMethod: number;
  deliveryEstimateEarly: string;
  deliveryEstimateLate: string;
  orderStatus: number;
};

const transportMap: Record<number, string> = {
  1: "Sea",
  2: "Rail",
  3: "Truck",
  4: "Air"
};

const orderStatusMap: Record<number, string> = {
  1: 'Created',
  2: 'Processing',
  3: 'Shipped', 
  4: 'Delivered', 
  5: 'Cancelled'
}

// Async wrapper to fetch orders
function OrdersList({ username }: { username: string }) {
  const [orders, setOrders] = useState<Order[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadOrders = async () => {
      try {
        const res = await fetch(`/api/track?username=${username}`);
        if (!res.ok) throw new Error(await res.text());
        const data = await res.json();
        setOrders(data);
      } catch (err: any) {
        setError(err.message || "Unknown error");
      }
    };

    loadOrders();
  }, [username]);

  if (error) return <p style={{ color: "red" }}>Error: {error}</p>;
  if (!orders) return <p>Loading orders...</p>;

  const estimatedDate = (orderDate: string, days: number) => {
    const d = new Date(orderDate);
    d.setDate(d.getDate() + days + 2); // +2 days buffer
    return d.toISOString().split("T")[0];
  };

  return (
    <table border={1} cellPadding={8}>
      <thead>
        <tr>
          <th>Parent #</th>
          <th>Order #</th>
          <th>Order Status</th>
          <th>Last Updated</th>
          <th>Start</th>
          <th>Current Location</th>
          <th>Destination</th>
          <th>Method of Transport</th>
          <th>Earliest Delivery</th>
          <th>Latest Delivery</th>
          <th>Order Placed</th>
        </tr>
      </thead>
      <tbody>
        {orders.map((order, i) => (
          <tr key={i}>
            <td>{order.parentNumber}</td>
            <td>{order.orderNumber}</td>
            <td>{orderStatusMap[order.orderStatus]}</td>
            <td>{order.orderLastUpdate}</td>
            <td>{order.startLocation}</td>
            <td>{order.currentLocation}</td>
            <td>{order.targetLocation}</td>
            <td>{transportMap[order.transportationMethod]}</td>
            <td>{order.deliveryEstimateEarly}</td>
            <td>{order.deliveryEstimateLate}</td>
            <td>{order.orderDate}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}



// Main client component
function OrdersPage() {
  const searchParams = useSearchParams();
  const username = searchParams.get("username");

  if (!username) return <p>No username provided.</p>;

  return (
    <div style={{ padding: "40px" }}>
      <h1>Order Tracking</h1>
      <p>Logged in as: <b>{username}</b></p>

      <Suspense fallback={<p>Loading orders...</p>}>
        <OrdersList username={username} />
      </Suspense> 
    </div>
  );
}

export default function OrderWrapper(){

  return <Suspense fallback={<p>Loading user...</p>}>
            <OrdersPage />
          </Suspense>
}