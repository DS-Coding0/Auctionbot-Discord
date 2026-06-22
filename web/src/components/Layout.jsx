import { Outlet, useLocation, useNavigate } from 'react-router-dom'
import { useEffect, useState } from 'react'
import Sidebar from './Sidebar.jsx'
import client from '../api/client.js'

export default function Layout() {
  const [user, setUser] = useState(null)
  const location = useLocation()
  const navigate = useNavigate()

  useEffect(() => {
    let alive = true
    client.get('/me')
      .then((data) => { if (alive) setUser(data) })
      .catch(() => { if (alive) setUser(null) })
    return () => { alive = false }
  }, [location.pathname])

  useEffect(() => {
    const isLogin = location.pathname === '/login'
    if (!user && !isLogin) navigate('/login')
  }, [user, location.pathname, navigate])

  return (
    <div className="app-shell">
      <Sidebar user={user} />
      <main>
        <Outlet context={{ user, setUser }} />
      </main>
    </div>
  )
}