// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import 'babel-polyfill'

import Vue from 'vue'
import Vuex from 'vuex'
import AlertAlert from '@/services/alertAlert'

import App from './App'
import router from './router'
import store from './store'

// global components
import PageLoadingSVG from '@/components/PageLoadingSVG'
import ComponentLoadingSVG from '@/components/ComponentLoadingSVG'
import Modal from '@/components/Modal'

// filters
import currencyFilter from '@/services/currency'

import { Datetime } from 'vue-datetime'
import 'vue-datetime/dist/vue-datetime.css'
Vue.config.productionTip = false

Vue.use(Vuex)
Vue.use(AlertAlert)

Vue.component('PageLoadingSVG', PageLoadingSVG)
Vue.component('ComponentLoadingSVG', ComponentLoadingSVG)
Vue.component('Modal', Modal)
Vue.component('datetime', Datetime)
Vue.filter('currency', currencyFilter)

/* eslint-disable no-new */
new Vue({
  el: '#app',
  store,
  router,
  template: '<App/>',
  components: { App },
})
