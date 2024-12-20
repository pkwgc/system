const config = {
  // Development configuration
  development: {
    apiUrl: 'http://localhost:8000',
    wsUrl: 'ws://localhost:8000'
  },
  // Production configuration
  production: {
    apiUrl: 'https://your-deployed-backend-url',
    wsUrl: 'wss://your-deployed-backend-url'
  }
}

// Set current environment
const ENV = 'development'

module.exports = {
  apiUrl: config[ENV].apiUrl,
  wsUrl: config[ENV].wsUrl
}
