import { useEffect, useState } from 'react'
import DashboardCard from '../components/DashboardCard.jsx'
import client from '../api/client.js'

export default function Auctions() {
  const [auctions, setAuctions] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let alive = true
    client.get('/auctions')
      .then((data) => {
        if (!alive) return
        setAuctions(Array.isArray(data) ? data : [])
      })
      .catch((err) => {
        if (!alive) return
        setError(err.message || 'Failed to load auctions')
      })
      .finally(() => {
        if (alive) setLoading(false)
      })
    return () => { alive = false }
  }, [])

  return (
    <div className="page auctions-page">
      <div className="page-header">
        <h1>Auctions</h1>
      </div>

      <div className="dashboard-grid">
        <DashboardCard title="Total auctions" value={auctions.length} />
        <DashboardCard title="Live auctions" value={auctions.filter((a) => a.status === 'live').length} />
        <DashboardCard title="Scheduled" value={auctions.filter((a) => a.status === 'scheduled').length} />
      </div>

      {loading && <p>Loading...</p>}
      {error && <p className="error">{error}</p>}

      {!loading && !error && (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Item</th>
                <th>Show</th>
                <th>Price</th>
                <th>Status</th>
                <th>Ends</th>
              </tr>
            </thead>
            <tbody>
              {auctions.map((auction) => (
                <tr key={auction.id}>
                  <td>{auction.id}</td>
                  <td>{auction.item_title || auction.item_id}</td>
                  <td>{auction.show_name || auction.show_id}</td>
                  <td>{auction.current_price}</td>
                  <td>{auction.status}</td>
                  <td>{auction.ends_at ? new Date(auction.ends_at).toLocaleString() : '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}