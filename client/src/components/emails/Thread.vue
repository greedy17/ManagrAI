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
      <div class="actions__item-header-title">{{ thread.subject }}</div>
      <div
        class="actions__item-header-date"
        style="display: flex; flex-direction: column; align-items: flex-end;"
      >
        <span
          :title="thread.last_message_timestamp | momentDateTimeShort"
          style="flex: 1; text-align: right;"
        >
          {{ (thread.last_message_timestamp * 1000) | timeAgo }}
        </span>
      </div>
      <div class="actions__item-header-action"></div>
    </div>

    <div class="actions__item-header" v-if="!isExpanded">
      <div class="actions__item-header-title">{{ thread.snippet }}</div>
    </div>
    <div v-if="isExpanded">
      <div v-if="isLoading" style="padding: 5rem;">
        <ComponentLoadingSVG />
      </div>
      <div v-if="!isLoading">
        <ThreadMessage
          :lead="lead"
          :message="message"
          @emailSent="emailSent"
          v-for="message in firstMessage"
          :key="message.id"
          :initiallyExpanded="true"
        ></ThreadMessage>
        <ThreadMessage
          :lead="lead"
          :message="message"
          @emailSent="emailSent"
          v-for="message in otherMessages"
          :key="message.id"
          :initiallyExpanded="false"
        ></ThreadMessage>
      </div>
    </div>
  </div>
</template>

<script>
import ThreadMessage from '@/components/emails/ThreadMessage'
import ComponentLoadingSVG from '@/components/ComponentLoadingSVG'
import Nylas from '@/services/nylas'

export default {
  name: 'Thread',
  components: { ThreadMessage, ComponentLoadingSVG },
  props: {
    thread: {
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
    if (this.initiallyExpanded) {
      this.getThreadMessages(this.thread.id)
    }
  },
  computed: {
    firstMessage() {
      return this.messages.filter((m, idx) => idx === 0)
    },
    otherMessages() {
      return this.messages.filter((m, idx) => idx > 0)
    },
  },
  methods: {
    toggleExpanded() {
      if (!this.isExpanded) {
        this.isExpanded = true
        this.isLoading = true
        this.getThreadMessages(this.thread.id)
      } else {
        this.isExpanded = false
      }
    },
    getThreadMessages(threadId) {
      Nylas.getThreadMessages(threadId)
        .then(response => {
          this.messages = response.data
          this.isLoading = false
        })
        .finally(() => {
          this.isLoading = false
        })
    },
    emailSent() {
      this.$emit('emailSent')
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
