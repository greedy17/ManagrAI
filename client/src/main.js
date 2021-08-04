import { datadogRum } from '@datadog/browser-rum'

datadogRum.init({
  applicationId: process.env.VUE_APP_DD_APP_ID,
  clientToken: process.env.VUE_APP_DD_CLIENT_TOKEN,
  site: 'datadoghq.com',
  service: 'managr',
  env: process.env.VUE_APP_DD_ENV,
  // Specify a version number to identify the deployed version of your application in Datadog
  // version: '1.0.0',
  sampleRate: 100,
  trackInteractions: true,
})

// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import 'babel-polyfill'

import Vue from 'vue'
import Vuex from 'vuex'
import AlertAlert from '@/services/alertAlert'
import VueMask from 'v-mask'
import * as VueGoogleMaps from 'vue2-google-maps'
import VueSanitize from 'vue-sanitize'

import App from './App'
import router from './router'
import store from './store'

// global components
import PageLoadingSVG from '@/components/PageLoadingSVG'
import ComponentLoadingSVG from '@/components/ComponentLoadingSVG'
import Modal from '@/components/Modal'
import '@/styles/vtooltip.scss'
import VTooltip from 'v-tooltip'
// filters
import { currencyFilter, currencyFilterNoCents } from '@/services/currency'
import { formatDateShort, constantToCapitalized } from '@/services/utils'
import {
  formatDateShortWithTime,
  momentDateTime,
  momentDateShort,
  momentDateTimeShort,
  timeAgo,
  toNumberSuffix,
  timeToNow,
  prependUrlProtocol,
  roundToOneDecimalPlace,
  snakeCaseToTextFilter,
  timeOnlyShort,
  toCapitalCase,
} from '@/services/filters'
import pluralize from 'pluralize'

import { Datetime } from 'vue-datetime'
import 'vue-datetime/dist/vue-datetime.css'
import vmodal from 'vue-js-modal'
Vue.config.productionTip = false

Vue.use(Vuex)
Vue.use(AlertAlert)
Vue.use(VueSanitize)
Vue.use(VueMask)
Vue.use(VueGoogleMaps, {
  load: {
    // NOTE (Bruno): Documentation for error-messages for this Google API:
    // https://developers.google.com/maps/documentation/javascript/error-messages
    key: process.env.VUE_APP_MAPS_API_KEY,
    libraries: 'places',
  },
})
Vue.use(VTooltip)
Vue.filter('momentDateTime', momentDateTime)
Vue.filter('momentDateTimeShort', momentDateTimeShort)
Vue.filter('momentDateShort', momentDateShort)
Vue.filter('currency', currencyFilter)
Vue.filter('currencyNoCents', currencyFilterNoCents)
Vue.filter('dateShort', formatDateShort)
Vue.filter('timeAgo', timeAgo)
Vue.filter('timeToNow', timeToNow)
Vue.filter('prependUrlProtocol', prependUrlProtocol)
Vue.filter('dateShortWithTime', formatDateShortWithTime)
Vue.filter('constantToCapitalized', constantToCapitalized)
Vue.filter('roundToOneDecimalPlace', roundToOneDecimalPlace)
Vue.filter('snakeCaseToTextFilter', snakeCaseToTextFilter)
Vue.filter('timeOnlyShort', timeOnlyShort)
Vue.filter('capitalCase', toCapitalCase)
Vue.filter('numberSuffix', toNumberSuffix)

Vue.filter('pluralize', function (value, number) {
  return pluralize(value, number)
})

Vue.component('PageLoadingSVG', PageLoadingSVG)
Vue.component('ComponentLoadingSVG', ComponentLoadingSVG)
Vue.component('Modal', Modal)

Vue.component('datetime', Datetime)
Vue.use(vmodal)

/* eslint-disable no-new */
new Vue({
  el: '#app',
  store,
  router,
  template: '<App/>',
  components: { App },
})
