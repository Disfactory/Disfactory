module.exports = {
  lintOnSave: false,
  devServer: {
    disableHostCheck: true,
    proxy: {
      '/server': {
        target: 'https://staging.disfactory.tw',
        changeOrigin: true,
        pathRewrite: {
          '^/server': ''
        }
      }
    }
  },
  pwa: {
    name: '農地違章工廠',
    themeColor: '#2196f3',
    workboxOptions: {
      skipWaiting: true,
      clientsClaim: true
    }
  },
  transpileDependencies: [
    'vuetify'
  ]
}
