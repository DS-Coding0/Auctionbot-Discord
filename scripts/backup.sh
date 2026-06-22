#!/bin/sh
pg_dump "$DATABASE_URL" > backup.sql