FROM node:20-alpine
WORKDIR /app
COPY web/package.json ./
RUN npm install
COPY web ./
EXPOSE 3001
CMD ["node", "server/index.js"]