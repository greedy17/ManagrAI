<template>
  <div class="actions__item">
    <div class="actions__row" @click="toggleExpanded()" style="cursor: pointer;">
      <div class="actions__item-header-icon">
        <img
          alt="icon"
          :src="require(`@/assets/images/message.svg`)"
          :class="{ 'filter-green': isExpanded }"
          class="icon"
        />
      </div>
      <div class="actions__item-header-title">
        Message Sent From:
        {{
          message.direction == 'SENT'
            ? message.createdByRef.fullName
            : 'number associated with ' + message.linkedContactsRef.map(c => c.fullName)
        }}
      </div>
      <div
        class="actions__item-header-date"
        style="display: flex; flex-direction: column; align-items: flex-end;"
      >
        <span
          :title="message.datetimeCreated | dateShortWithTime"
          style="flex: 1; text-align: right;"
        >
          {{ getFriendlyMessageDirection }}
        </span>
      </div>
      <div class="actions__item-header-action"></div>
    </div>

    <div class="actions__item-header" v-if="isExpanded">
      <div class="actions__item-header-title">{{ message.body }}</div>
      <br />
      <div
        class="actions__item-header-date"
        style="display: flex; flex-direction: column; align-items: flex-start;"
      >
        <span title="date-time-created" style="flex: 1; text-align: right;">
          {{ message.datetimeCreated | dateShortWithTime }}
        </span>
      </div>
      <div
        class="actions__item-header-date"
        style="display: flex; flex-direction: column; align-items: flex-end;"
      >
        <span title="status" style="flex: 1; text-align: right;">
          {{ getFriendlyMessageStatus }}
        </span>
      </div>
    </div>
    <div v-if="isExpanded"></div>
  </div>
</template>

<script>
/***
 *
 * Special component for rendering message from LeadMessage object rather than twilio
 *
 *
 */
export default {
  name: 'Message',
  components: {},
  props: {
    message: {
      type: Object,
      required: true,
    },
    initiallyExpanded: {
      type: Boolean,
      required: false,
      default: false,
    },
    lead: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      isExpanded: false,
      isLoading: true,
      messages: {},
    }
  },
  created() {
    this.isExpanded = this.initiallyExpanded
  },
  computed: {
    getFriendlyMessageDirection() {
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
    },
  },
  methods: {
    toggleExpanded() {
      if (!this.isExpanded) {
        this.isExpanded = true
      } else {
        this.isExpanded = false
      }
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/layout';
@import '@/styles/containers';
@import '@/styles/forms';
.filter-green {
  filter: invert(45%) sepia(96%) saturate(2978%) hue-rotate(123deg) brightness(92%) contrast(80%);
}
</style>
