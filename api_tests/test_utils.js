const request = require('request');
const deasync = require('deasync');
const util = require('util');
const config = require('./config');

let login = ((username, password) => {
    let uri = get_request_uri('auth/jwt-token-auth/', true);
    let options = {
        uri: uri,
        json: {
            username: username,
            password: password
        }
    };
    return new Promise((resolve, reject) => {
        request.post(uri, options, (err, resp, body) => {
            if (err) {
                throw (err);
            }
            else if (!body || !body.token) {
                throw ("Something went wrong when logging in. No token found.")
            }
            global.token = body.token;
            resolve(body.token);
        });
    });
});

let loginAsync = ((username, password, refresh = false) => {
    if (refresh) {
        global.token = undefined;
    }
    if (!global.token) {
        console.log("Attempting to login...");
        login(username, password)
            .then(t => {
                console.log("Login Successful!")
            })
            .catch(err => {
                console.log("Login failed:");
                console.log(err);
            })
    }
    deasync.loopWhile(() => { return !global.token; })
    return global.token;
});

let get_request_uri = (api_path, exclude_version = false) => {
    let uri = util.format("%s:%s/%s/%s", config.host, config.port, config.version, api_path);
    if (exclude_version) {
        uri = uri.replace('/' + config.version, '');
    }
    return uri;
}

module.exports = {
    login: loginAsync,
    get_request_uri: get_request_uri
}
