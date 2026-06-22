import { useNavigate } from 'react-router-dom'

export default function LoginButton() {
  const navigate = useNavigate()

  const handleLogin = () => {
    window.location.href = '/auth/discord'
  }

  const handleLogout = async () => {
    await fetch('/auth/logout', { method: 'POST', credentials: 'include' })
    navigate('/login')
    window.location.reload()
  }

  return (
    <div className="login-actions">
      <button type="button" onClick={handleLogin}>Login with Discord</button>
      <button type="button" onClick={handleLogout}>Logout</button>
    </div>
  )
}