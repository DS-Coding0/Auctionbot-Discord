import { Router } from 'express'
import { query, transaction } from '../db.js'

const router = Router()

router.get('/', async (req, res, next) => {
  try {
    const result = await query(
      `SELECT a.id, a.show_id, a.item_id, a.channel_id, a.message_id, a.current_price, a.status, a.ends_at, a.created_at,
              i.title AS item_title,
              sh.name AS show_name
       FROM auctions a
       JOIN items i ON i.id = a.item_id
       JOIN shows sh ON sh.id = a.show_id
       ORDER BY a.created_at DESC`
    )
    res.json(result.rows)
  } catch (error) {
    next(error)
  }
})

router.get('/:id', async (req, res, next) => {
  try {
    const { id } = req.params
    const result = await query(
      `SELECT a.id, a.show_id, a.item_id, a.channel_id, a.message_id, a.current_price, a.status, a.ends_at, a.created_at,
              i.title AS item_title,
              sh.name AS show_name
       FROM auctions a
       JOIN items i ON i.id = a.item_id
       JOIN shows sh ON sh.id = a.show_id
       WHERE a.id = $1`,
      [id]
    )
    if (result.rowCount === 0) return res.status(404).json({ error: 'Auction not found' })
    res.json(result.rows[0])
  } catch (error) {
    next(error)
  }
})

router.post('/', async (req, res, next) => {
  try {
    const { show_id, item_id, channel_id = null, message_id = null, current_price, status = 'scheduled', ends_at = null } = req.body
    if (!show_id || !item_id || current_price === undefined) {
      return res.status(400).json({ error: 'Missing required fields' })
    }

    const result = await transaction(async (client) => {
      const auction = await client.query(
        `INSERT INTO auctions (show_id, item_id, channel_id, message_id, current_price, status, ends_at)
         VALUES ($1, $2, $3, $4, $5, $6, $7)
         RETURNING *`,
        [show_id, item_id, channel_id, message_id, current_price, status, ends_at]
      )
      return auction.rows[0]
    })

    res.status(201).json(result)
  } catch (error) {
    next(error)
  }
})

router.patch('/:id', async (req, res, next) => {
  try {
    const { id } = req.params
    const allowed = ['show_id', 'item_id', 'channel_id', 'message_id', 'current_price', 'status', 'ends_at']
    const fields = []
    const values = []
    let idx = 1

    for (const key of allowed) {
      if (req.body[key] !== undefined) {
        fields.push(`${key} = $${idx}`)
        values.push(req.body[key])
        idx++
      }
    }

    if (fields.length === 0) {
      return res.status(400).json({ error: 'No fields to update' })
    }

    values.push(id)
    const result = await query(
      `UPDATE auctions SET ${fields.join(', ')} WHERE id = $${idx} RETURNING *`,
      values
    )
    if (result.rowCount === 0) return res.status(404).json({ error: 'Auction not found' })
    res.json(result.rows[0])
  } catch (error) {
    next(error)
  }
})

router.post('/:id/start', async (req, res, next) => {
  try {
    const { id } = req.params
    const result = await query(
      `UPDATE auctions SET status = 'live' WHERE id = $1 RETURNING *`,
      [id]
    )
    if (result.rowCount === 0) return res.status(404).json({ error: 'Auction not found' })
    res.json(result.rows[0])
  } catch (error) {
    next(error)
  }
})

router.post('/:id/stop', async (req, res, next) => {
  try {
    const { id } = req.params
    const result = await query(
      `UPDATE auctions SET status = 'ended' WHERE id = $1 RETURNING *`,
      [id]
    )
    if (result.rowCount === 0) return res.status(404).json({ error: 'Auction not found' })
    res.json(result.rows[0])
  } catch (error) {
    next(error)
  }
})

router.delete('/:id', async (req, res, next) => {
  try {
    const { id } = req.params
    const result = await query('DELETE FROM auctions WHERE id = $1 RETURNING id', [id])
    if (result.rowCount === 0) return res.status(404).json({ error: 'Auction not found' })
    res.json({ ok: true })
  } catch (error) {
    next(error)
  }
})

export default router