import client from './client.js'

export const getItems = () => client.get('/items')
export const getItem = (id) => client.get(`/items/${id}`)
export const createItem = (payload) => client.post('/items', payload)
export const updateItem = (id, payload) => client.patch(`/items/${id}`, payload)
export const deleteItem = (id) => client.delete(`/items/${id}`)