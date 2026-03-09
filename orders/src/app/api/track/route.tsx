import { NextResponse } from "next/server";

export async function GET(request: Request) {

  const { searchParams } = new URL(request.url);
  const username = searchParams.get("username");

  const orders = [
    {
      username,
      parentNumber: "P100",
      orderNumber: "O101",
      orderDate: "2026-03-01",
      currentLocation: "Canada",
      targetLocation: "United States",
      distKM: 800,
      transportMethod: 2,
      estimateDays: 4
    },
    {
      username,
      parentNumber: "P200",
      orderNumber: "O202",
      orderDate: "2026-03-02",
      currentLocation: "China",
      targetLocation: "Japan",
      distKM: 2000,
      transportMethod: 0,
      estimateDays: 8
    },
    {
      username,
      parentNumber: "P300",
      orderNumber: "O303",
      orderDate: "2026-03-03",
      currentLocation: "China",
      targetLocation: "United States",
      distKM: 11000,
      transportMethod: 3,
      estimateDays: 2
    }
  ];

  return NextResponse.json(orders);
}