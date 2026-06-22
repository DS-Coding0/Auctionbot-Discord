export default function DashboardCard({ title, value, subtitle }) {
  return (
    <div className="dashboard-card">
      <h3>{title}</h3>
      <div className="dashboard-card-value">{value}</div>
      {subtitle ? <p>{subtitle}</p> : null}
    </div>
  )
}