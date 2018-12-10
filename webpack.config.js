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
      "./node_modules/jquery/dist/jquery.min.js",
    ],
    site: [
      "./node_modules/materialize-css/sass/materialize.scss",
      rootAssetPath + "/scss/security.scss",
      rootAssetPath + "/scss/site.scss"
    ],
    app_admin: [
      rootAssetPath + "/scss/security.scss",
      rootAssetPath + "/js/admin.js",
      rootAssetPath + "/scss/app.scss",
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
    new CopyWebpackPlugin([{
      from: rootAssetPath + '/partials',
      to: './partials',
      ignore: [ '*.html~' ]
    }]),
    new CopyWebpackPlugin([{
      from: rootAssetPath + '/images',
      to: './images'
    }])
  ]
}
