#!/bin/sh
psql "$DATABASE_URL" < backup.sql