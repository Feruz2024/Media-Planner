FROM node:20-alpine
WORKDIR /app
COPY package.json pnpm-lock.yaml* ./
RUN npm install -g pnpm && pnpm install
COPY . /app
EXPOSE 3000
CMD ["pnpm","dev","--host"]
