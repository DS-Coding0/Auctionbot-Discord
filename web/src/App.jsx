import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout.jsx'
import Dashboard from './pages/Dashboard.jsx'
import Shows from './pages/Shows.jsx'
import Items from './pages/Items.jsx'
import Auctions from './pages/Auctions.jsx'
import Orders from './pages/Orders.jsx'
import Login from './pages/Login.jsx'

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/shows" element={<Shows />} />
        <Route path="/items" element={<Items />} />
        <Route path="/auctions" element={<Auctions />} />
        <Route path="/orders" element={<Orders />} />
      </Route>
      <Route path="/login" element={<Login />} />
    </Routes>
  )
}