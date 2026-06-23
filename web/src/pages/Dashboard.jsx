import { useEffect, useState } from 'react'
import { useOutletContext } from 'react-router-dom'
import { getOrders } from '../api/orders.js'
import client from '../api/client.js'

export default function Dashboard() {
  const { user } = useOutletContext()
  const [orders, setOrders] = useState([])
  const [auctions, setAuctions] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let alive = true

    async function load() {
      try {
        const [orderData, auctionData] = await Promise.all([
          getOrders('all'),
          client.get('/auctions')
        ])
        if (!alive) return
        setOrders(Array.isArray(orderData) ? orderData : [])
        setAuctions(Array.isArray(auctionData) ? auctionData : [])
      } catch (error) {
        console.error('Dashboard load failed:', error)
        if (alive) {
          setOrders([])
          setAuctions([])
        }
      } finally {
        if (alive) setLoading(false)
      }
    }

    load()
    return () => { alive = false }
  }, [])

  return (
    <div className="page dashboard">
      <h1>Dashboard</h1>
      {loading ? (
        <p>Loading...</p>
      ) : (
        <>
          <section>
            <h2>Login status</h2>
            <p>{user ? `Logged in as ${user.global_name || user.username}` : 'Not logged in'}</p>
          </section>

          <section>
            <h2>Orders</h2>
            <p>Total: {orders.length}</p>
          </section>

          <section>
            <h2>Recent auctions</h2>
            <ul>
              {auctions.slice(0, 5).map((auction) => (
                <li key={auction.id}>
                  {auction.item_title || auction.item_id} — {auction.status}
                </li>
              ))}
            </ul>
          </section>
        </>
      )}
    </div>
  )
}