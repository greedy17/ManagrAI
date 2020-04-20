// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import 'babel-polyfill'

import Vue from 'vue'
import Vuex from 'vuex'
import AlertAlert from 'vue-alert-alert'

import App from './App'
import router from './router'
import store from './store'
import NavBar from '@/components/NavBar'

Vue.config.productionTip = false

Vue.use(Vuex)
Vue.use(AlertAlert)

Vue.component('NavBar', NavBar)

/* eslint-disable no-new */
new Vue({
  el: '#app',
  store,
  router,
  template: '<App/>',
  components: { App },
})
