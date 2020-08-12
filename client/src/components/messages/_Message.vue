<template>
  <div class="message">
    <span class="muted">
      {{ message.dateCreated | dateShortWithTime }}
    </span>
    <span class="message__body">
      {{ message.body }}
    </span>
    <span class="muted message-status">
      {{ message.status }}
    </span>
  </div>
</template>

<script>
/**
 *
 * Special Component for Twilio Messages
 */
export default {
  name: 'Message',
  components: {},
  props: {
    message: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {}
  },
  created() {},

  methods: {},
}
</script>

<style lang="scss" scoped>
@import '@/styles/layout';
@import '@/styles/containers';
@import '@/styles/forms';
.message {
  display: flex;
  flex-direction: column;
  font-size: 18px;
  > * {
    margin: 1rem 0rem;
  }
}
.muted {
  font-size: 10px;
}
.message-status {
  text-align: right;
}
</style>
