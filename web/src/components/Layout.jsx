import { Outlet, useLocation, useNavigate } from 'react-router-dom'
import { useEffect, useState } from 'react'
import Sidebar from './Sidebar.jsx'
import client from '../api/client.js'

export default function Layout() {
  const [user, setUser] = useState(undefined)
  const location = useLocation()
  const navigate = useNavigate()

  useEffect(() => {
    let alive = true

    client.get('/me')
      .then((data) => {
        if (alive) setUser(data)
      })
      .catch((error) => {
        console.error('Failed to load /me:', error)
        if (alive) setUser(null)
      })

    return () => {
      alive = false
    }
  }, [])

  useEffect(() => {
    const isLogin = location.pathname === '/login'
    if (user === undefined) return
    if (!user && !isLogin) navigate('/login', { replace: true })
  }, [user, location.pathname, navigate])

  if (user === undefined && location.pathname !== '/login') {
    return (
      <div className="app-shell">
        <main>
          <p>Loading...</p>
        </main>
      </div>
    )
  }

  return (
    <div className="app-shell">
      <Sidebar user={user} />
      <main>
        <Outlet context={{ user, setUser }} />
      </main>
    </div>
  )
}