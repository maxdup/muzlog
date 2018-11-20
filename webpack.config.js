var path = require('path');
var webpack = require('webpack');
const CopyWebpackPlugin = require('copy-webpack-plugin');

var rootAssetPath = './muzsite'

module.exports = {
  mode: 'development',
  watch: true,
  entry: {
    vendor: [
      "./node_modules/reset-css/sass/_reset.scss",
    ],
    base: [
      rootAssetPath + "/scss/security.scss",
    ],
    app: [
      rootAssetPath + "/scss/security.scss",
      rootAssetPath + "/scss/app.scss",
      rootAssetPath + "/js/app.js",
    ],
    app_admin: [
      rootAssetPath + "/scss/security.scss",
      rootAssetPath + "/scss/app.scss",
      rootAssetPath + "/js/admin.js",
    ],
  },
  output: {
    path: __dirname + "/muzsite/static",
    publicPath: 'http://0.0.0.0:5000/static/',
    filename: "[name].js"
  },
  resolve: {
    extensions: ['.js', '.css'],
    modules: ["node_modules"],
  },
  module: {
     rules: [
      { test: /\.css$/,
        use: [{ loader: "style-loader" },
              { loader: "css-loader" }]},
      { test: /\.scss$/,
        use: [{ loader: "style-loader" }, // creates style nodes from JS strings
              { loader: "css-loader" }, // translates CSS into CommonJS
              { loader: "sass-loader", // compiles Sass to CSS, using Node Sass by default
                options: {
                  includePaths: ["node_modules/reset-css/sass"]
                }
              }]
      }]
  },
  plugins: [
    new webpack.ProvidePlugin({
      $: 'jquery',
      jQuery: 'jquery',
      "window.jQuery": "jquery"
    }),
    new CopyWebpackPlugin([
      { from: rootAssetPath + '/partials',
        to: './partials'}
    ])
  ]
}
