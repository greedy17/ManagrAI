// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import 'babel-polyfill'

import Vue from 'vue'
import Vuex from 'vuex'
// import AlertAlert from 'vue-alert-alert'
import AlertAlert from '@/services/alertAlert'

import App from './App'
import router from './router'
import store from './store'

// global components
import NavBar from '@/components/NavBar'
import LoadingSVG from '@/components/LoadingSVG'

// filters
import currencyFilter from '@/services/currency'

Vue.config.productionTip = false

Vue.use(Vuex)
Vue.use(AlertAlert)

Vue.component('NavBar', NavBar)
Vue.component('LoadingSVG', LoadingSVG)

Vue.filter('currency', currencyFilter)

/* eslint-disable no-new */
new Vue({
  el: '#app',
  store,
  router,
  template: '<App/>',
  components: { App },
})
