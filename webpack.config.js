const path = require('path');
const ExtractTextPlugin = require("extract-text-webpack-plugin");

module.exports = {
  entry: {
    index: './assets/index.js',
    teams: './assets/javascript/illumidesk/teams.js',
    IllumiDesk: './assets/javascript/illumidesk/IllumiDesk.js',
    'object-lifecycle': './assets/javascript/illumidesk/examples/object-lifecycle.js',
  },
  output: {
    path: path.resolve(__dirname, './static'),
    filename: 'js/[name]-bundle.js',
    library: ["SiteJS", "[name]"],
  },
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /(node_modules|bower_components)/,
        loader: "babel-loader",
        options: { presets: ["@babel/env"] }
      },
      {
        test: /\.scss$/,
        use: ExtractTextPlugin.extract({
          fallback: 'style-loader',
          use: [
            'css-loader',
            'sass-loader'
          ]
        })
    }]
  },
  plugins: [
    new ExtractTextPlugin('css/site.css'),
  ]
};
