CREATE TABLE IF NOT EXISTS servers (
  id BIGSERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS users (
  id BIGSERIAL PRIMARY KEY,
  discord_id VARCHAR(64) UNIQUE NOT NULL,
  username VARCHAR(255) NOT NULL,
  global_name VARCHAR(255),
  avatar VARCHAR(1024),
  role VARCHAR(32) NOT NULL DEFAULT 'buyer',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS shows (
  id BIGSERIAL PRIMARY KEY,
  server_id BIGINT NOT NULL REFERENCES servers(id) ON DELETE CASCADE,
  seller_id BIGINT NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  status VARCHAR(32) NOT NULL DEFAULT 'draft',
  starts_at TIMESTAMPTZ,
  ends_at TIMESTAMPTZ,
  voice_channel_id BIGINT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS items (
  id BIGSERIAL PRIMARY KEY,
  show_id BIGINT NOT NULL REFERENCES shows(id) ON DELETE CASCADE,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  image_url VARCHAR(1024),
  start_price NUMERIC(10,2) NOT NULL DEFAULT 0,
  instant_buy_price NUMERIC(10,2),
  min_increment NUMERIC(10,2) NOT NULL DEFAULT 1,
  status VARCHAR(32) NOT NULL DEFAULT 'draft',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT items_start_price_nonnegative CHECK (start_price >= 0),
  CONSTRAINT items_instant_buy_price_nonnegative CHECK (
    instant_buy_price IS NULL OR instant_buy_price >= 0
  ),
  CONSTRAINT items_min_increment_positive CHECK (min_increment > 0),
  CONSTRAINT items_instant_buy_ge_start CHECK (
    instant_buy_price IS NULL OR instant_buy_price >= start_price
  )
);

CREATE TABLE IF NOT EXISTS auctions (
  id BIGSERIAL PRIMARY KEY,
  show_id BIGINT NOT NULL REFERENCES shows(id) ON DELETE CASCADE,
  item_id BIGINT NOT NULL REFERENCES items(id) ON DELETE CASCADE,
  channel_id VARCHAR(64),
  message_id VARCHAR(64),
  current_price NUMERIC(10,2) NOT NULL DEFAULT 0,
  highest_bidder_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'scheduled',
  ends_at TIMESTAMPTZ,
  highest_bidder_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
  reset_seconds INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT auctions_item_unique UNIQUE (item_id),
  CONSTRAINT auctions_current_price_nonnegative CHECK (current_price >= 0)
);

CREATE TABLE IF NOT EXISTS bids (
  id BIGSERIAL PRIMARY KEY,
  auction_id BIGINT NOT NULL REFERENCES auctions(id) ON DELETE CASCADE,
  buyer_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  amount NUMERIC(10,2) NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT bids_amount_positive CHECK (amount > 0)
);

CREATE TABLE IF NOT EXISTS orders (
  id BIGSERIAL PRIMARY KEY,
  buyer_id BIGINT NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
  seller_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
  item_id BIGINT NOT NULL REFERENCES items(id) ON DELETE RESTRICT,
  auction_id BIGINT REFERENCES auctions(id) ON DELETE SET NULL,
  quantity INTEGER NOT NULL DEFAULT 1,
  total_price NUMERIC(10,2) NOT NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'pending',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT orders_quantity_positive CHECK (quantity > 0),
  CONSTRAINT orders_total_price_nonnegative CHECK (total_price >= 0)
);

CREATE TABLE IF NOT EXISTS ratings (
  id BIGSERIAL PRIMARY KEY,
  show_id BIGINT REFERENCES shows(id) ON DELETE CASCADE,
  order_id BIGINT REFERENCES orders(id) ON DELETE SET NULL,
  rater_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  target_user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  score INTEGER NOT NULL CHECK (score BETWEEN 1 AND 5),
  comment TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT ratings_unique_per_order UNIQUE (order_id, rater_id)
);

CREATE TABLE IF NOT EXISTS seller_banned_buyers (
  id BIGSERIAL PRIMARY KEY,
  seller_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  buyer_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  reason TEXT,
  active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT seller_banned_buyers_unique UNIQUE (seller_id, buyer_id)
);

CREATE TABLE IF NOT EXISTS audit_logs (
  id BIGSERIAL PRIMARY KEY,
  type VARCHAR(64) NOT NULL,
  entity_type VARCHAR(64),
  entity_id VARCHAR(64),
  message TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_discord_id
  ON users(discord_id);

CREATE INDEX IF NOT EXISTS idx_shows_server_id
  ON shows(server_id);

CREATE INDEX IF NOT EXISTS idx_shows_seller_id
  ON shows(seller_id);

CREATE INDEX IF NOT EXISTS idx_shows_status
  ON shows(status);

CREATE INDEX IF NOT EXISTS idx_items_show_id
  ON items(show_id);

CREATE INDEX IF NOT EXISTS idx_items_status
  ON items(status);

CREATE INDEX IF NOT EXISTS idx_auctions_show_id
  ON auctions(show_id);

CREATE INDEX IF NOT EXISTS idx_auctions_status
  ON auctions(status);

CREATE INDEX IF NOT EXISTS idx_auctions_ends_at
  ON auctions(ends_at);

CREATE INDEX IF NOT EXISTS idx_auctions_highest_bidder_id
  ON auctions(highest_bidder_id);

CREATE INDEX IF NOT EXISTS idx_bids_auction_id
  ON bids(auction_id);

CREATE INDEX IF NOT EXISTS idx_bids_buyer_id
  ON bids(buyer_id);

CREATE INDEX IF NOT EXISTS idx_bids_auction_amount_created
  ON bids(auction_id, amount DESC, created_at ASC);

CREATE INDEX IF NOT EXISTS idx_orders_buyer_id
  ON orders(buyer_id);

CREATE INDEX IF NOT EXISTS idx_orders_seller_id
  ON orders(seller_id);

CREATE INDEX IF NOT EXISTS idx_orders_item_id
  ON orders(item_id);

CREATE INDEX IF NOT EXISTS idx_orders_auction_id
  ON orders(auction_id);

CREATE INDEX IF NOT EXISTS idx_orders_status
  ON orders(status);

CREATE UNIQUE INDEX IF NOT EXISTS uq_orders_one_per_auction
  ON orders(auction_id)
  WHERE auction_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_ratings_target_user_id
  ON ratings(target_user_id);

CREATE INDEX IF NOT EXISTS idx_ratings_rater_id
  ON ratings(rater_id);

CREATE INDEX IF NOT EXISTS idx_ratings_order_id
  ON ratings(order_id);

CREATE INDEX IF NOT EXISTS idx_seller_banned_buyers_seller_active
  ON seller_banned_buyers(seller_id, active);

CREATE INDEX IF NOT EXISTS idx_audit_logs_type
  ON audit_logs(type);

CREATE INDEX IF NOT EXISTS idx_audit_logs_entity
  ON audit_logs(entity_type, entity_id);

CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at
  ON audit_logs(created_at);