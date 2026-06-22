import client from './client.js'

export const getRatings = (params = '') => client.get(`/ratings${params}`)
export const createRating = (payload) => client.post('/ratings', payload)