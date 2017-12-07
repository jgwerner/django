const request = require('request');
const deasync = require('deasync');
const util = require('util');
const config = require('./config');

let login = ((username, password) => {
    let uri = util.format('%s/%s', config.base_address, 'auth/jwt-token-auth/')
    let options = {
        json: {
            username: username,
            password: password
        }        
    }
    return new Promise((resolve, reject) => {
        request.post(uri, options, (err, resp, body) => {
            if (err) {
                throw(err);
            }
            else if (!body || !body.token) {
                throw("Something went wrong when logging in. No token found.")
            }
            resolve(body.token);
        });
    });
});

let loginAsync = ((username, password) => {
    login_done = false;
    token = ''
    console.log("Attempting to login to api-backend...");
    login(username, password)
        .then(t => {
            console.log("Login Successful!")
            token = t;
            login_done = true;
        })
        .catch(err => {
            console.log("Login failed:");
            console.log(err);
        })
    deasync.loopWhile(() => { return !login_done; })
    return token;
});

module.exports = {
    login: loginAsync
}