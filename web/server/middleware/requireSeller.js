export default function requireSeller(req, res, next) {
  if (!req.user) {
    return res.status(401).json({ error: 'Unauthorized' })
  }

  const roles = Array.isArray(req.user.roles) ? req.user.roles : []
  const isSeller = roles.includes('seller') || roles.includes('admin')

  if (!isSeller) {
    return res.status(403).json({ error: 'Forbidden' })
  }

  next()
}