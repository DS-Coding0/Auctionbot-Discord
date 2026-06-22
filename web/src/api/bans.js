import client from './client.js'

export const getBans = (sellerId = '') => client.get(`/bans${sellerId ? `?seller_id=${encodeURIComponent(sellerId)}` : ''}`)
export const upsertBan = (payload) => client.post('/bans', payload)
export const updateBan = (id, payload) => client.patch(`/bans/${id}`, payload)