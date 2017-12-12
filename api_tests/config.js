const config = {
    host: process.env.HOST || 'http://localhost',
    port: process.env.PORT || '80',
    username: process.env.TEST_USER || 'admin',
    password: process.env.TEST_USER_PASSWORD || 'admin',
    email: process.env.TEST_USER_EMAIL || 'admin@example.com',
    version: process.env.API_VERSION || 'v1'
}

module.exports = config;