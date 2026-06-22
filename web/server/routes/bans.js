import { Router } from 'express'
import requireAuth from '../middleware/requireAuth.js'
import requireSeller from '../middleware/requireSeller.js'
import { query } from '../db.js'

const router = Router()

router.get('/', requireAuth, async (req, res, next) => {
  try {
    const sellerId = req.query.seller_id || req.user.id
    const result = await query(
      `SELECT id, seller_id, buyer_id, reason, active, created_at, updated_at
       FROM seller_banned_buyers
       WHERE seller_id = $1
       ORDER BY created_at DESC`,
      [sellerId]
    )
    res.json(result.rows)
  } catch (e) { next(e) }
})

router.post('/', requireSeller, async (req, res, next) => {
  try {
    const { buyer_id, reason = null, active = true } = req.body
    if (!buyer_id) return res.status(400).json({ error: 'Missing buyer_id' })
    const result = await query(
      `INSERT INTO seller_banned_buyers (seller_id, buyer_id, reason, active)
       VALUES ($1, $2, $3, $4)
       ON CONFLICT (seller_id, buyer_id)
       DO UPDATE SET reason = EXCLUDED.reason, active = EXCLUDED.active, updated_at = NOW()
       RETURNING id, seller_id, buyer_id, reason, active, created_at, updated_at`,
      [req.user.id, buyer_id, reason, active]
    )
    res.status(201).json(result.rows[0])
  } catch (e) { next(e) }
})

router.patch('/:id', requireSeller, async (req, res, next) => {
  try {
    const { id } = req.params
    const { reason = null, active = true } = req.body
    const result = await query(
      `UPDATE seller_banned_buyers
       SET reason = $1, active = $2, updated_at = NOW()
       WHERE id = $3 AND seller_id = $4
       RETURNING id, seller_id, buyer_id, reason, active, created_at, updated_at`,
      [reason, active, id, req.user.id]
    )
    if (result.rowCount === 0) return res.status(404).json({ error: 'Ban not found' })
    res.json(result.rows[0])
  } catch (e) { next(e) }
})

export default router