import { Router } from 'express'
import { query } from '../db.js'

const router = Router()

router.get('/', async (req, res, next) => {
  try {
    const { limit = 100, type = null } = req.query
    const params = []
    let sql = `SELECT id, type, entity_type, entity_id, message, created_at
               FROM audit_logs`

    if (type) {
      params.push(type)
      sql += ` WHERE type = $${params.length}`
    }

    sql += ` ORDER BY created_at DESC LIMIT $${params.length + 1}`
    params.push(Number(limit) || 100)

    const result = await query(sql, params)
    res.json(result.rows)
  } catch (error) {
    next(error)
  }
})

router.get('/:id', async (req, res, next) => {
  try {
    const { id } = req.params
    const result = await query(
      `SELECT id, type, entity_type, entity_id, message, created_at
       FROM audit_logs
       WHERE id = $1`,
      [id]
    )
    if (result.rowCount === 0) return res.status(404).json({ error: 'Log entry not found' })
    res.json(result.rows[0])
  } catch (error) {
    next(error)
  }
})

router.post('/', async (req, res, next) => {
  try {
    const { type, entity_type = null, entity_id = null, message } = req.body
    if (!type || !message) {
      return res.status(400).json({ error: 'Missing required fields' })
    }

    const result = await query(
      `INSERT INTO audit_logs (type, entity_type, entity_id, message)
       VALUES ($1, $2, $3, $4)
       RETURNING id, type, entity_type, entity_id, message, created_at`,
      [type, entity_type, entity_id, message]
    )

    res.status(201).json(result.rows[0])
  } catch (error) {
    next(error)
  }
})

router.delete('/:id', async (req, res, next) => {
  try {
    const { id } = req.params
    const result = await query('DELETE FROM audit_logs WHERE id = $1 RETURNING id', [id])
    if (result.rowCount === 0) return res.status(404).json({ error: 'Log entry not found' })
    res.json({ ok: true })
  } catch (error) {
    next(error)
  }
})

export default router