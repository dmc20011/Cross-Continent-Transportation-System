'use client'
import { useRouter } from 'next/navigation'

export default function Home() {
  const router = useRouter()

  const handleCreateOrder = () => {
    router.push('/createOrder')  // Goes to localhost:3000/createOrder
  }

  const handleTrackOrder = (username: string) => {
    router.push(`/api/track?username=${username}`)  // e.g. Goes to localhost:3000/api/track?username=john
  }

  return (
    <div className="">
      <h1 className="">Shipping App</h1>
      
      {/* Button to create order */}
      <button 
        onClick={handleCreateOrder}
        className=""
      >
        Create New Shipping Order
      </button>

      {/* Track order form */}
      <div className="">
        <input 
          id="username"
          type="text" 
          placeholder="Enter username"
          className=""
        />
        <button 
          onClick={() => {
            const username = (document.getElementById('username') as HTMLInputElement).value
            if (username) handleTrackOrder(username)
          }}
          className=""
        >
          Track Order
        </button>
      </div>
    </div>
  )
}
