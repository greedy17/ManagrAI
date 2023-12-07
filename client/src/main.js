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
// import VueSSE from 'vue-sse';
// import AlertAlert from '@/services/alertAlert'
import * as VueGoogleMaps from 'vue2-google-maps'
import App from './App'
import router from './router'
import store from './store'

// global components
import Modal from '@/components/Modal'
import { Datetime } from 'vue-datetime'
import 'vue-datetime/dist/vue-datetime.css'
import vmodal from 'vue-js-modal'
import VueClipboard from 'vue-clipboard2'
import { Drag, Drop } from 'vue-drag-drop';
import outsideClickDirective from "@/services/directives/outside-click";
import Toast from "vue-toastification";
import "vue-toastification/dist/index.css";
import VueSanitize from "vue-sanitize";
import VueApexCharts from 'vue-apexcharts'

import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { library } from '@fortawesome/fontawesome-svg-core'
import { faBars, faCircleUser, faRocket, faCog, faHeadphones, faUser, faSquareXmark, faShuffle, faRotate, faFilter, faSquareCaretLeft, faBolt, faAt, faUserGroup, faUserPlus, faCalendarPlus, faStairs, faSackDollar, faSignature, faLayerGroup, faAnglesRight, } from '@fortawesome/free-solid-svg-icons'
import { faEnvelope, faFileLines, faPaperPlane, faSquarePlus, faCalendar } from '@fortawesome/free-regular-svg-icons'
import { faSalesforce, faHubspot } from '@fortawesome/free-brands-svg-icons'
import { loadStripe } from '@stripe/stripe-js';


let defaults = VueSanitize.defaults;
// defaults.allowedTags = defaults.allowedTags.filter(t => t === 'br' || t === 'li');

Vue.use(VueSanitize);

Vue.config.productionTip = false;

Vue.directive("outside-click", outsideClickDirective);
Vue.config.productionTip = false

Vue.use(Toast);
Vue.use(VueClipboard)
Vue.use(Vuex)
// Vue.use(AlertAlert)
Vue.use(VueGoogleMaps, {
  load: {
    // NOTE (Bruno): Documentation for error-messages for this Google API:
    // https://developers.google.com/maps/documentation/javascript/error-messages
    key: process.env.VUE_APP_MAPS_API_KEY,
    libraries: 'places',
  },
})
Vue.use(VueApexCharts)
// Vue.use(VueSSE);

library.add(faBars, faSquarePlus, faPaperPlane, faCircleUser, faRocket, faCog, faHeadphones, faUser, faSquareXmark, faShuffle, faRotate, faFilter, faSquareCaretLeft, faSalesforce, faBolt, faAt, faUserGroup, faUserPlus, faCalendarPlus, faCalendar, faStairs, faSackDollar, faSignature, faLayerGroup, faEnvelope, faFileLines, faAnglesRight, faHubspot)

Vue.component('apexchart', VueApexCharts)
Vue.component('drag', Drag);
Vue.component('drop', Drop);
Vue.component('Modal', Modal)
Vue.component('datetime', Datetime)
Vue.component('vue-multiselect')
Vue.component('font-awesome-icon', FontAwesomeIcon)
Vue.use(vmodal)

let stripePromise = null;

export async function getStripe() {
  if (!stripePromise) {
    const key = store.state.stripeKey
    stripePromise = loadStripe(key);
  }
  return stripePromise;
}

const StripePlugin = {
  install(VueInstance) {
    VueInstance.prototype.$stripe = getStripe;
  },
};

Vue.use(StripePlugin);


/* eslint-disable no-new */
new Vue({
  el: '#app',
  store,
  router,
  template: '<App/>',
  components: { App },
})
