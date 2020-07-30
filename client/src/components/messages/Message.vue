<template>
  <div class="actions__item">
    <div class="actions__row" @click="toggleExpanded()" style="cursor: pointer;">
      <div class="actions__item-header-icon">
        <img
          alt="icon"
          :src="require(`@/assets/images/email.svg`)"
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
          :title="message.datetimeCreated | momentDateTimeShort"
          style="flex: 1; text-align: right;"
        >
          {{ (message.datetimeCreated * 1000) | timeAgo }}
        </span>
      </div>
      <div class="actions__item-header-action"></div>
    </div>

    <div class="actions__item-header" v-if="isExpanded">
      <div class="actions__item-header-title">{{ message.body }}</div>
    </div>
    <div v-if="isExpanded"></div>
  </div>
</template>

<script>
import ThreadMessage from '@/components/emails/ThreadMessage'
import ComponentLoadingSVG from '@/components/ComponentLoadingSVG'

export default {
  name: 'Message',
  components: { ThreadMessage, ComponentLoadingSVG },
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
  computed: {},
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
