import { Router } from 'express'
import { query, transaction } from '../db.js'

const router = Router()

router.get('/', async (req, res, next) => {
  try {
    const result = await query(
      `SELECT s.id, s.name, s.scheduled_at, s.voice_channel_id, s.status, s.created_at, srv.guild_id, srv.name AS server_name
       FROM shows s
       JOIN servers srv ON srv.id = s.server_id
       ORDER BY s.scheduled_at DESC`
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
      `SELECT s.id, s.name, s.scheduled_at, s.voice_channel_id, s.status, s.created_at, srv.guild_id, srv.name AS server_name
       FROM shows s
       JOIN servers srv ON srv.id = s.server_id
       WHERE s.id = $1`,
      [id]
    )
    if (result.rowCount === 0) return res.status(404).json({ error: 'Show not found' })
    res.json(result.rows[0])
  } catch (error) {
    next(error)
  }
})

router.post('/', async (req, res, next) => {
  try {
    const { guild_id, server_name, name, scheduled_at, voice_channel_id = null, created_by } = req.body
    if (!guild_id || !server_name || !name || !scheduled_at || !created_by) {
      return res.status(400).json({ error: 'Missing required fields' })
    }

    const result = await transaction(async (client) => {
      const server = await client.query(
        `INSERT INTO servers (guild_id, name)
         VALUES ($1, $2)
         ON CONFLICT (guild_id) DO UPDATE SET name = EXCLUDED.name
         RETURNING id, guild_id, name`,
        [guild_id, server_name]
      )

      const show = await client.query(
        `INSERT INTO shows (server_id, name, scheduled_at, voice_channel_id, status, created_by)
         VALUES ($1, $2, $3, $4, 'scheduled', $5)
         RETURNING *`,
        [server.rows[0].id, name, scheduled_at, voice_channel_id, created_by]
      )

      return { server: server.rows[0], show: show.rows[0] }
    })

    res.status(201).json(result)
  } catch (error) {
    next(error)
  }
})

router.patch('/:id', async (req, res, next) => {
  try {
    const { id } = req.params
    const fields = []
    const values = []
    let idx = 1

    for (const key of ['name', 'scheduled_at', 'voice_channel_id', 'status']) {
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
      `UPDATE shows SET ${fields.join(', ')} WHERE id = $${idx} RETURNING *`,
      values
    )
    if (result.rowCount === 0) return res.status(404).json({ error: 'Show not found' })
    res.json(result.rows[0])
  } catch (error) {
    next(error)
  }
})

router.delete('/:id', async (req, res, next) => {
  try {
    const { id } = req.params
    const result = await query('DELETE FROM shows WHERE id = $1 RETURNING id', [id])
    if (result.rowCount === 0) return res.status(404).json({ error: 'Show not found' })
    res.json({ ok: true })
  } catch (error) {
    next(error)
  }
})

export default router