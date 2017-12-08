const config = {
    host: process.env.HOST || 'http://localhost',
    port: process.env.PORT || '80',
    username: process.env.TEST_USER || 'AutoTester',
    password: process.env.TEST_USER_PASSWORD || 'Aut0123!',
    email: process.env.TEST_USER_EMAIL || 'AutoTester@domain.com',
    version: process.env.API_VERSION || 'v1'
}

module.exports = config;