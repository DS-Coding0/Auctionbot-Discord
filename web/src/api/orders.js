import client from './client.js'

export function getOrders() {
  return client.get('/orders')
}