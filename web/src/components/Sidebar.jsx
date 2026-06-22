import { NavLink, useNavigate } from 'react-router-dom'

export default function Sidebar({ user }) {
  const navigate = useNavigate()

  const handleLogout = async () => {
    await fetch('/auth/logout', { method: 'POST', credentials: 'include' })
    navigate('/login')
    window.location.reload()
  }

  return (
    <aside className="sidebar">
      <div className="sidebar-user">
        {user ? (
          <>
            <strong>{user.global_name || user.username}</strong>
            <span>@{user.username}</span>
            <button type="button" onClick={handleLogout}>Logout</button>
          </>
        ) : (
          <span>Not logged in</span>
        )}
      </div>
      <nav>
        <NavLink to="/">Dashboard</NavLink>
        <NavLink to="/shows">Shows</NavLink>
        <NavLink to="/items">Items</NavLink>
        <NavLink to="/auctions">Auctions</NavLink>
        <NavLink to="/orders">Orders</NavLink>
      </nav>
    </aside>
  )
}