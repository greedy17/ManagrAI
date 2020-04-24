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
import store, { removeAlert } from './store'
import Alert from './alerts'
import AlertAlertItem from './AlertAlertItem.vue'

export default {
  name: 'AlertAlert',
  components: {
    AlertAlertItem,
  },
  props: {
    top: {
      required: true,
      type: Number,
    },
  },
  data() {
    return {
      alert: Alert.create({
        type: 'info',
        message: 'test',
      }),
      alerts: store.alerts,
    }
  },
  methods: {
    handleRemove(alert) {
      removeAlert(alert)
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
