const path = require('path');
// const CopyPlugin = require('copy-webpack-plugin');
module.exports = {
   mode: "development",
   entry: { airbnb: './src/ts/airbnb.ts' },
   output: {
      path: path.join(__dirname, "src/server/static/js"),
      filename: "[name].js",
   },
   resolve: {
      extensions: [".ts", ".js"],
   },
   module: {
      rules: [
         {
            test: /\.tsx?$/,
            loader: "ts-loader",
            exclude: /node_modules/,
         },
      ],
   },
   devtool: 'source-map',
   plugins: [
      // new CopyPlugin({
      //    patterns: [
      //       // { from: ".", to: ".", context: "public" },
      //       { from: 'src/css', to: '../css' },
      //       { from: 'src/html', to: '../html' },
      //       { from: 'src/images', to: '../images' },
      //       { from: 'src/manifest.json', to: '../manifest.json' }
      //    ],
      // }),
   ],
};