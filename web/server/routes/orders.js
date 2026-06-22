import { Router } from 'express'
import { query, transaction } from '../db.js'
import requireAuth from '../middleware/requireAuth.js'
import requireSeller from '../middleware/requireSeller.js'

const router = Router()

router.get('/', requireAuth, async (req, res, next) => {
  try {
    const { role = 'all' } = req.query
    const userId = req.user.id

    let sql = `SELECT o.id, o.buyer_id, o.seller_id, o.item_id, o.auction_id, o.quantity, o.total_price, o.status, o.created_at,
                      i.title AS item_title,
                      b.username AS buyer_username,
                      s.username AS seller_username
               FROM orders o
               JOIN items i ON i.id = o.item_id
               LEFT JOIN users b ON b.id = o.buyer_id
               LEFT JOIN users s ON s.id = o.seller_id`
    const params = []

    if (role === 'buyer') {
      params.push(userId)
      sql += ` WHERE o.buyer_id = $1`
    } else if (role === 'seller') {
      params.push(userId)
      sql += ` WHERE o.seller_id = $1`
    } else {
      params.push(userId, userId)
      sql += ` WHERE o.buyer_id = $1 OR o.seller_id = $2`
    }

    sql += ` ORDER BY o.created_at DESC`
    const result = await query(sql, params)
    res.json(result.rows)
  } catch (error) {
    next(error)
  }
})

router.get('/:id', requireAuth, async (req, res, next) => {
  try {
    const { id } = req.params
    const result = await query(
      `SELECT o.id, o.buyer_id, o.seller_id, o.item_id, o.auction_id, o.quantity, o.total_price, o.status, o.created_at,
              i.title AS item_title,
              b.username AS buyer_username,
              s.username AS seller_username
       FROM orders o
       JOIN items i ON i.id = o.item_id
       LEFT JOIN users b ON b.id = o.buyer_id
       LEFT JOIN users s ON s.id = o.seller_id
       WHERE o.id = $1`,
      [id]
    )
    if (result.rowCount === 0) return res.status(404).json({ error: 'Order not found' })
    const order = result.rows[0]
    if (order.buyer_id !== req.user.id && order.seller_id !== req.user.id && !req.user.roles?.includes('admin')) {
      return res.status(403).json({ error: 'Forbidden' })
    }
    res.json(order)
  } catch (error) {
    next(error)
  }
})

router.post('/', requireAuth, async (req, res, next) => {
  try {
    const { item_id, auction_id = null, quantity = 1, total_price, seller_id = null } = req.body
    if (!item_id || total_price === undefined) {
      return res.status(400).json({ error: 'Missing required fields' })
    }

    const result = await transaction(async (client) => {
      const order = await client.query(
        `INSERT INTO orders (buyer_id, seller_id, item_id, auction_id, quantity, total_price, status)
         VALUES ($1, $2, $3, $4, $5, $6, 'pending')
         RETURNING *`,
        [req.user.id, seller_id, item_id, auction_id, quantity, total_price]
      )
      return order.rows[0]
    })

    res.status(201).json(result)
  } catch (error) {
    next(error)
  }
})

router.patch('/:id', requireAuth, async (req, res, next) => {
  try {
    const { id } = req.params
    const allowed = ['status', 'quantity', 'total_price']
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

    const existing = await query('SELECT buyer_id, seller_id FROM orders WHERE id = $1', [id])
    if (existing.rowCount === 0) return res.status(404).json({ error: 'Order not found' })
    const order = existing.rows[0]
    const isOwner = order.buyer_id === req.user.id || order.seller_id === req.user.id || req.user.roles?.includes('admin')
    const canEdit = isOwner || req.user.roles?.includes('seller')
    if (!canEdit) return res.status(403).json({ error: 'Forbidden' })

    values.push(id)
    const result = await query(`UPDATE orders SET ${fields.join(', ')} WHERE id = $${idx} RETURNING *`, values)
    res.json(result.rows[0])
  } catch (error) {
    next(error)
  }
})

router.delete('/:id', requireSeller, async (req, res, next) => {
  try {
    const { id } = req.params
    const result = await query('DELETE FROM orders WHERE id = $1 RETURNING id', [id])
    if (result.rowCount === 0) return res.status(404).json({ error: 'Order not found' })
    res.json({ ok: true })
  } catch (error) {
    next(error)
  }
})

export default router