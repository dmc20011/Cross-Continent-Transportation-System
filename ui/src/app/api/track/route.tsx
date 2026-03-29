import { NextResponse } from "next/server";

const NEXT_PUBLIC_API = process.env.NEXT_PUBLIC_API_TRACK;

console.log(`Got api: ${NEXT_PUBLIC_API}`)

if (!NEXT_PUBLIC_API){
  throw new Error("Missing API variable");
}

const API = NEXT_PUBLIC_API.concat("/tracking/");
console.log(API)
export async function GET(request: Request) {

  const { searchParams } = new URL(request.url);
  const username = searchParams.get("username");

  const res = await fetch(API + username);

  if (!res.ok) {
    throw new Error("Failed to fetch orders");
  }
  
  const ordersJson = await res.json();
  //extract list of orders
  const orders = ordersJson["orders"];
  console.log(orders);

  return NextResponse.json(orders);
}