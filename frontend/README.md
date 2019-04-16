# IllumiDesk Web UI

[![codecov](https://codecov.io/gh/IllumiDesk/app-backend/branch/master/graph/badge.svg?token=hYg2cWoCkZ)](https://codecov.io/gh/IllumiDesk/app-backend)
[![Build Status](https://travis-ci.com/IllumiDesk/app-backend.svg?token=y3jvxynhJQZHELnDYJdy&branch=master)](https://travis-ci.com/IllumiDesk/app-backend)

An API-agnostic frontend for IllumiDesk in ReactJs.

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

## Getting Started

Clone repo and install dependencies:

```
git clone https://github.com/illumidesk/app-backend/
cd app-backend
cd frontend
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
