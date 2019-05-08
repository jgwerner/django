# IllumiDesk Web UI

![Build Status](https://travis-ci.com/IllumiDesk/illumidesk.svg?token=y3jvxynhJQZHELnDYJdy&branch=master)](https://travis-ci.com/IllumiDesk/illumidesk)

An API-agnostic frontend for IllumiDesk in ReactJs.

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

## Getting Started

Clone repo and install dependencies:

```
git clone https://github.com/illumidesk/illumidesk/
cd illumidesk
cd app-frontend
npm install
```

Run application in development:

```
npm run start
```

Test:

```
npm test
```

## Environment Variables

The tables below describes the environment variables that can be passed in at build time:

### General Settings

| Variable Name | Required | Default Value | Description |
| ------------- | :------: | :-----------: | ----------- |
| `REACT_APP_API_URL` | Yes | `null` | The URL for the IllumiDesk API with which the application should interact. |
