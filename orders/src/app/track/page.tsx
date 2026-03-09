"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";

type Order = {
  parentNumber: string;
  orderNumber: string;
  currentLocation: string;
  targetLocation: string;
  transportMethod: number;
  estimateDays: number;
  orderDate: string;
};

const transportMap: Record<number, string> = {
  0: "Boat",
  1: "Train",
  2: "Truck",
  3: "Plane"
};

export default function OrdersPage() {

  const searchParams = useSearchParams();
  const username = searchParams.get("username");

  const [orders, setOrders] = useState<Order[]>([]);

  useEffect(() => {

    if (!username) return;

    const loadOrders = async () => {

      const res = await fetch(`/api/track?username=${username}`);

      if (!res.ok) {
        console.error("API error:", await res.text());
        return;
      }

      const data = await res.json();
      setOrders(data);
    };

    loadOrders();

  }, [username]);

  const estimatedDate = (orderDate: string, days: number) => {
    const d = new Date(orderDate);
    d.setDate(d.getDate() + days + 2); // + 2 for wait before shipping
    return d.toISOString().split("T")[0];
  };

  return (
    <div style={{ padding: "40px" }}>

      <h1>Order Tracking</h1>

      <p>Logged in as: <b>{username}</b></p>

      <table border={1} cellPadding={8}>
        <thead>
          <tr>
            <th>Parent #</th>
            <th>Order #</th>
            <th>Destination</th>
            <th>Current Location</th>
            <th>Method of Transport</th>
            <th>Estimated Delivery Date</th>
          </tr>
        </thead>

        <tbody>
          {orders.map((order, i) => (
            <tr key={i}>
              <td>{order.parentNumber}</td>
              <td>{order.orderNumber}</td>
              <td>{order.targetLocation}</td>
              <td>{order.currentLocation}</td>
              <td>{transportMap[order.transportMethod]}</td>
              <td>{estimatedDate(order.orderDate, order.estimateDays)}</td>
            </tr>
          ))}
        </tbody>

      </table>
    </div>
  );
}