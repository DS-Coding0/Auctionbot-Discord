import express from 'express'
import session from 'express-session'
import cors from 'cors'
import dotenv from 'dotenv'
import passport from 'passport'
import { Strategy as DiscordStrategy } from 'passport-discord'

import authRouter from './auth.js'
import meRouter from './routes/me.js'
import showsRouter from './routes/shows.js'
import itemsRouter from './routes/items.js'
import auctionsRouter from './routes/auctions.js'
import ordersRouter from './routes/orders.js'
import logsRouter from './routes/logs.js'
import ratingsRouter from './routes/ratings.js'
import bansRouter from './routes/bans.js'

import requireAuth from './middleware/requireAuth.js'
import { initDb } from './db.js'

dotenv.config()

const app = express()
const PORT = process.env.PORT || 3001
const CLIENT_URL = process.env.CLIENT_URL || 'http://localhost:5173'

app.set('trust proxy', 1)

app.use(cors({ origin: CLIENT_URL, credentials: true }))
app.use(express.json())
app.use(express.urlencoded({ extended: true }))
app.use(session({
  secret: process.env.SESSION_SECRET || 'dev-secret',
  resave: false,
  saveUninitialized: false,
  cookie: {
    httpOnly: true,
    sameSite: 'lax',
    secure: true
  }
}))

app.use(passport.initialize())
app.use(passport.session())

passport.serializeUser((user, done) => done(null, user))
passport.deserializeUser((obj, done) => done(null, obj))

passport.use(new DiscordStrategy({
  clientID: process.env.DISCORD_CLIENT_ID,
  clientSecret: process.env.DISCORD_CLIENT_SECRET,
  callbackURL: process.env.DISCORD_CALLBACK_URL,
  scope: ['identify', 'guilds']
}, async (accessToken, refreshToken, profile, done) => {
  try {
    return done(null, {
      id: profile.id,
      username: profile.username,
      discriminator: profile.discriminator,
      global_name: profile.global_name,
      avatar: profile.avatar,
      accessToken
    })
  } catch (error) {
    return done(error)
  }
}))

app.get('/health', (req, res) => {
  res.json({ ok: true, service: 'web-server' })
})

app.use('/api/auth', authRouter)

app.use('/api/me', meRouter)
app.use('/api/shows', requireAuth, showsRouter)
app.use('/api/items', requireAuth, itemsRouter)
app.use('/api/auctions', requireAuth, auctionsRouter)
app.use('/api/orders', requireAuth, ordersRouter)
app.use('/api/logs', requireAuth, logsRouter)
app.use('/api/ratings', ratingsRouter)
app.use('/api/bans', bansRouter)

app.use((req, res) => {
  res.status(404).json({ error: 'Not found' })
})

app.use((error, req, res, next) => {
  console.error(error)
  res.status(500).json({ error: 'Internal server error' })
})

await initDb()
app.listen(PORT, () => {
  console.log(`Web server running on ${PORT}`)
})