module.exports = {
  lintOnSave: false,
  devServer: {
    proxy: {
      '/server': {
        target: 'https://middle2.disfactory.tw',
        changeOrigin: true,
        pathRewrite: {
          '^/server': ''
        }
      }
    }
  }
}
