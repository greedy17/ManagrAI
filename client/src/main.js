// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import 'babel-polyfill'

import Vue from 'vue'
import Vuex from 'vuex'

import App from './App'
import router from './router'
import store from './store'
import NavBar from '@/components/NavBar'

Vue.config.productionTip = false

Vue.use(Vuex)
Vue.component('NavBar', NavBar)

/* eslint-disable no-new */
new Vue({
	el: '#app',
	store,
	router,
	template: '<App/>',
	components: { App },
})
