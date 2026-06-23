import client from './client.js'

export function getAuctions() {
  return client.get('/auctions')
}