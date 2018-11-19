var path = require('path');
var webpack = require('webpack');
const CopyWebpackPlugin = require('copy-webpack-plugin');

var rootAssetPath = './muzsite'
module.exports = {
  mode: 'development',
  watch: true,
  entry: {
    vendor: [ "./node_modules/jquery/dist/jquery.js",
              "./node_modules/reset-css/sass/_reset.scss",
              "./node_modules/materialize-css/sass/materialize.scss",
              "./node_modules/materialize-css/dist/js/materialize.js"],
    flask_security: [ rootAssetPath + "/scss/security.scss" ],
    app: [ rootAssetPath + "/js/app.js",
           rootAssetPath + "/scss/app.scss"],
  },
  output: {
    path: __dirname + "/muzsite/static",
    publicPath: 'http://0.0.0.0:5000/static/',
    filename: "[name].js"
  },
  resolve: {
    extensions: ['.js', '.css']
  },
  module: {
    rules: [{
      test: /\.scss$/,
      use: [{ loader: "style-loader"}, // creates style nodes from JS strings
            { loader: "css-loader"}, // translates CSS into CommonJS
            { loader: "sass-loader", // compiles Sass to CSS, using Node Sass by default
              options: {
                includePaths: ["node_modules/reset-css/sass"]
              }
            }]
    }]
  },
  plugins: [
    new CopyWebpackPlugin([
      { from: rootAssetPath + '/partials',
        to: './partials'}
    ])
  ]
}
