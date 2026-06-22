import { Router } from 'express'

const router = Router()

router.get('/', async (req, res) => {
  if (!req.user) {
    return res.json(null)
  }

  res.json({
    id: req.user.id,
    username: req.user.username,
    discriminator: req.user.discriminator,
    global_name: req.user.global_name,
    avatar: req.user.avatar
  })
})

router.get('/session', async (req, res) => {
  res.json({ authenticated: !!req.user })
})

export default router