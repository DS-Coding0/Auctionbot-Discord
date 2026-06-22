import { Router } from 'express'
import { query, transaction } from '../db.js'

const router = Router()

router.get('/', async (req, res, next) => {
  try {
    const result = await query(
      `SELECT i.id, i.show_id, i.seller_id, i.category, i.title, i.description, i.image_url, i.starting_price, i.buy_now_price, i.status, i.created_at,
              s.name AS show_name,
              u.display_name AS seller_name
       FROM items i
       LEFT JOIN shows s ON s.id = i.show_id
       LEFT JOIN users u ON u.id = i.seller_id
       ORDER BY i.created_at DESC`
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
      `SELECT i.id, i.show_id, i.seller_id, i.category, i.title, i.description, i.image_url, i.starting_price, i.buy_now_price, i.status, i.created_at,
              s.name AS show_name,
              u.display_name AS seller_name
       FROM items i
       LEFT JOIN shows s ON s.id = i.show_id
       LEFT JOIN users u ON u.id = i.seller_id
       WHERE i.id = $1`,
      [id]
    )
    if (result.rowCount === 0) return res.status(404).json({ error: 'Item not found' })
    res.json(result.rows[0])
  } catch (error) {
    next(error)
  }
})

router.post('/', async (req, res, next) => {
  try {
    const {
      show_id,
      seller_id,
      category,
      title,
      description,
      image_url = null,
      starting_price,
      buy_now_price = null,
      status = 'draft'
    } = req.body

    if (!show_id || !seller_id || !category || !title || !description || starting_price === undefined) {
      return res.status(400).json({ error: 'Missing required fields' })
    }

    const result = await transaction(async (client) => {
      const item = await client.query(
        `INSERT INTO items (show_id, seller_id, category, title, description, image_url, starting_price, buy_now_price, status)
         VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
         RETURNING *`,
        [show_id, seller_id, category, title, description, image_url, starting_price, buy_now_price, status]
      )
      return item.rows[0]
    })

    res.status(201).json(result)
  } catch (error) {
    next(error)
  }
})

router.patch('/:id', async (req, res, next) => {
  try {
    const { id } = req.params
    const allowed = ['show_id', 'seller_id', 'category', 'title', 'description', 'image_url', 'starting_price', 'buy_now_price', 'status']
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
      `UPDATE items SET ${fields.join(', ')} WHERE id = $${idx} RETURNING *`,
      values
    )
    if (result.rowCount === 0) return res.status(404).json({ error: 'Item not found' })
    res.json(result.rows[0])
  } catch (error) {
    next(error)
  }
})

router.delete('/:id', async (req, res, next) => {
  try {
    const { id } = req.params
    const result = await query('DELETE FROM items WHERE id = $1 RETURNING id', [id])
    if (result.rowCount === 0) return res.status(404).json({ error: 'Item not found' })
    res.json({ ok: true })
  } catch (error) {
    next(error)
  }
})

export default router