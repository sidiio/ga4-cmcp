FROM node:20-slim

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Expose port for SSE
EXPOSE 8080

# Run using tsx
CMD ["npx", "tsx", "src/index.ts"]
