import { Router } from 'express'
import passport from 'passport'

const router = Router()
const CLIENT_URL = process.env.CLIENT_URL || 'http://localhost:5173'

router.get('/discord', passport.authenticate('discord'))

router.get(
  '/discord/callback',
  passport.authenticate('discord', { failureRedirect: '/api/auth/failed' }),
  (req, res, next) => {
    req.session.save((err) => {
      if (err) return next(err)
      res.redirect(`${CLIENT_URL}/dashboard`)
    })
  }
)

router.get('/failed', (req, res) => {
  res.status(401).json({ error: 'Discord authentication failed' })
})

router.post('/logout', (req, res) => {
  req.logout(() => {
    req.session.destroy(() => res.json({ ok: true }))
  })
})

export default router