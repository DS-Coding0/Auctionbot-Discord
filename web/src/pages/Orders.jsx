import { useEffect, useMemo, useState } from 'react'
import { getOrders } from '../api/orders.js'

export default function Orders() {
  const [role, setRole] = useState('all')
  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let alive = true
    setLoading(true)
    setError('')
    getOrders(role)
      .then((data) => {
        if (!alive) return
        setOrders(Array.isArray(data) ? data : [])
      })
      .catch((err) => {
        if (!alive) return
        setError(err.message || 'Failed to load orders')
      })
      .finally(() => {
        if (alive) setLoading(false)
      })
    return () => { alive = false }
  }, [role])

  const counts = useMemo(() => ({ total: orders.length }), [orders])

  return (
    <div className="page">
      <div className="page-header">
        <h1>Orders</h1>
        <select value={role} onChange={(e) => setRole(e.target.value)}>
          <option value="all">All</option>
          <option value="buyer">Buyer</option>
          <option value="seller">Seller</option>
        </select>
      </div>

      <p className="muted">Total: {counts.total}</p>

      {loading && <p>Loading...</p>}
      {error && <p className="error">{error}</p>}

      {!loading && !error && (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Item</th>
                <th>Buyer</th>
                <th>Seller</th>
                <th>Qty</th>
                <th>Total</th>
                <th>Status</th>
                <th>Created</th>
              </tr>
            </thead>
            <tbody>
              {orders.map((order) => (
                <tr key={order.id}>
                  <td>{order.id}</td>
                  <td>{order.item_title || order.item_id}</td>
                  <td>{order.buyer_username || order.buyer_id}</td>
                  <td>{order.seller_username || order.seller_id}</td>
                  <td>{order.quantity}</td>
                  <td>{order.total_price}</td>
                  <td>{order.status}</td>
                  <td>{order.created_at ? new Date(order.created_at).toLocaleString() : '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}