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
  },
  chainWebpack: config => {
    if (process.env.NODE_ENV === 'development') {
      config
        .output
        .filename('[name].[hash].js')
        .end()
    }
  },
  pwa: {
    name: 'Disfactory',
    themeColor: '#2196f3',
    workboxOptions: {
      skipWaiting: true,
      clientsClaim: true
    }
  }
}
