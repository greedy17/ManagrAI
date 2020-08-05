<template>
  <div class="message">
    <span class="muted">
      {{ message.dateCreated | dateShortWithTime }}
    </span>
    <span class="message__body">
      {{ message.body }}
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
  computed: {
    /*     getFriendlyMessageDirection() {
      switch (this.message.direction) {
        case 'SENT':
          return 'outbound'
        case 'RECEIVED':
          return 'inbound'
        default:
          return 'N/A'
      }
    },
    getFriendlyMessageStatus() {
      switch (this.message.status) {
        case 'DELIVERED':
          return 'This Message was delivered'

        case 'NOT_DELIVERED':
          return 'Not able to deliver this message'

        case 'MESSAGE_PENDING':
          return 'This message is still processing'

        default:
          return 'Devlivery Information unavailable '
      }
    }, */
  },
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
</style>
