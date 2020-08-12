<template>
  <div class="aa-container" :style="{ top: `${top}px` }">
    <transition-group name="fade" tag="div">
      <alert-alert-item
        v-for="alert in alerts"
        :alert="alert"
        :key="alert.id"
        @remove="handleRemove"
      >
      </alert-alert-item>
    </transition-group>
  </div>
</template>

<script>
import throttle from 'lodash.throttle'
import store, { removeAlert } from './store'
import AlertAlertItem from './AlertAlertItem.vue'

export default {
  name: 'AlertAlert',
  components: {
    AlertAlertItem,
  },
  data() {
    return {
      top: this.oneRem * 0.5,
      alerts: store.alerts,
    }
  },
  mounted() {
    // NOTE (Bruno 4-23-20): this listener is never removed because it only needs to be removed on tab close, which happens automatically
    document.addEventListener('scroll', throttle(this.setTop, 30))
    this.setTop()
  },
  methods: {
    handleRemove(alert) {
      removeAlert(alert)
    },
    setTop() {
      // NOTE (Bruno 4-23-20): querySelector is used to gather DOM data, not manipulate it
      let nav = document.querySelector('#nav')
      if (!nav) {
        this.top = this.oneRem * 0.5
        return
      }
      let navRect = nav.getBoundingClientRect()
      let calculation = navRect.height + navRect.top
      let calculationIsValid = navRect.height >= calculation && calculation >= 0
      let margin = this.oneRem * 0.5
      if (calculationIsValid && calculation + margin !== this.top) {
        this.top = calculation + margin
      }

      return calculationIsValid
    },
  },
  computed: {
    oneRem() {
      return parseInt(window.getComputedStyle(document.querySelector('html')).fontSize)
    },
  },
}
</script>

<style scoped>
.aa-container {
  width: 100vw;
  display: flex;
  flex-flow: column;
  align-items: center;
  z-index: 1001;
  position: fixed;
}

/*
 * Item transition animations
 */
.fade-move {
  transition: all 600ms ease-in-out 50ms;
}
.fade-enter-active {
  transition: all 300ms ease-out;
}

.fade-leave-active {
  transition: all 200ms ease-in;
  position: absolute;
  z-index: 0;
}

.fade-enter,
.fade-leave-to {
  opacity: 0;
}
.fade-enter {
  transform: scale(0.9);
}
</style>
