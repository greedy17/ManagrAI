module.exports = {
  runtimeCompiler: true,
  assetsDir: 'static',
  devServer: {
    proxy: {
      '/api/': {
        target:
          (process.env.VUE_APP_DEV_SERVER_BACKEND || 'https://mymanagrapp-staging.herokuapp.com') +
          '/api/',
        changeOrigin: true,
        pathRewrite: {
          '^/api': '',
        },
      },
    },
  },
}
