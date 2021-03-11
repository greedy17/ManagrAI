module.exports = {
  runtimeCompiler: true,
  assetsDir: 'static',
  devServer: {
    proxy: {
      '/api/': {
        target: (process.env.VUE_APP_DEV_SERVER_BACKEND || 'https://staging-2.managr.ai') + '/api/',
        changeOrigin: true,
        pathRewrite: {
          '^/api': '',
        },
      },
    },
  },
}
