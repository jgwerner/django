const path = require('path');
const ExtractTextPlugin = require("extract-text-webpack-plugin");

module.exports = {
  entry: {
    index: './assets/index.js',
    teams: './assets/js/illumidesk/teams.js',
    IllumiDesk: './assets/js/illumidesk/IllumiDesk.js',
  },
  output: {
    path: path.resolve(__dirname, './staticfiles'),
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
