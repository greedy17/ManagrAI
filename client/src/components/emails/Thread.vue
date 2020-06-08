<template>
  <div class="actions__item">
    <div class="actions__row">
      <div class="actions__item-header-icon">
        <img
          alt="icon"
          :src="require(`@/assets/images/email.svg`)"
          @click="toggleExpanded()"
          :class="{ 'filter-green': isExpanded }"
          class="icon"
        />
      </div>
      <div class="actions__item-header-title">{{ thread.subject }}</div>
      <div class="actions__item-header-date">
        {{ thread.last_message_timestamp | momentDateTimeShort }}
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
          :message="message"
          @emailSent="emailSent"
          v-for="(message, index) in messages"
          :key="message.id"
          v-if="index === 0"
          :initiallyExpanded="true"
        ></ThreadMessage>
        <ThreadMessage
          :message="message"
          @emailSent="emailSent"
          v-for="(message, index) in messages"
          :key="message.id"
          v-if="index > 0"
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
