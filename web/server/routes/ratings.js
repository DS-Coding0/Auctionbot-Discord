import { Router } from 'express'
import requireAuth from '../middleware/requireAuth.js'
import { query } from '../db.js'

const router = Router()

router.get('/', requireAuth, async (req, res, next) => {
  try {
    const { target_user_id = null, show_id = null } = req.query
    const params = []
    let sql = `SELECT id, show_id, order_id, rater_id, target_user_id, score, comment, created_at
               FROM ratings`
    const where = []
    if (target_user_id) { params.push(target_user_id); where.push(`target_user_id = $${params.length}`) }
    if (show_id) { params.push(show_id); where.push(`show_id = $${params.length}`) }
    if (where.length) sql += ` WHERE ${where.join(' AND ')}`
    sql += ` ORDER BY created_at DESC`
    const result = await query(sql, params)
    res.json(result.rows)
  } catch (e) { next(e) }
})

router.post('/', requireAuth, async (req, res, next) => {
  try {
    const { show_id = null, order_id = null, target_user_id, score, comment = null } = req.body
    if (!target_user_id || !score) return res.status(400).json({ error: 'Missing required fields' })
    const result = await query(
      `INSERT INTO ratings (show_id, order_id, rater_id, target_user_id, score, comment)
       VALUES ($1, $2, $3, $4, $5, $6)
       RETURNING id, show_id, order_id, rater_id, target_user_id, score, comment, created_at`,
      [show_id, order_id, req.user.id, target_user_id, score, comment]
    )
    res.status(201).json(result.rows[0])
  } catch (e) { next(e) }
})

export default router