module.exports = {
  runtimeCompiler: true,
  assetsDir: 'static',
  devServer: {
    proxy: {
      '/api/': {
        target: (process.env.VUE_APP_DEV_SERVER_BACKEND || '{staging_full_url}') + '/api/',
        changeOrigin: true,
        pathRewrite: {
          '^/api': '',
        },
      },
    },
  },
}
