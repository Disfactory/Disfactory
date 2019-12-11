module.exports = {
  lintOnSave: false,
  devServer: {
    proxy: {
      '/server': {
        target: 'https://api.disfactory.tw',
        changeOrigin: true,
        pathRewrite: {
          '^/server': ''
        }
      }
    }
  }
}
