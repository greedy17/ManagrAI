import store, { addAlert, removeAlert } from './store'
import AlertAlert from './AlertAlert.vue'

const Plugin = {
  install(Vue) {
    Vue.prototype.$Alert = {
      alert: addAlert,
      remove: removeAlert,
      alerts: store.alerts,
      nextAlertID: store.nextAlertID,
    }
    Vue.component(AlertAlert.name, AlertAlert)
  },
}

export default Plugin
