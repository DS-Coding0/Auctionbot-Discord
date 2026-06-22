import client from './client.js'

export const getShows = () => client.get('/shows')
export const getShow = (id) => client.get(`/shows/${id}`)
export const createShow = (payload) => client.post('/shows', payload)
export const updateShow = (id, payload) => client.patch(`/shows/${id}`, payload)
export const deleteShow = (id) => client.delete(`/shows/${id}`)