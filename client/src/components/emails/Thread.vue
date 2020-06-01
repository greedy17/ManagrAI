<template>
  <div class="actions__item">
    <div class="actions__item-header">
      <div class="actions__item-header-icon">
        <img
          alt="icon"
          :src="require(`@/assets/images/email.svg`)"
          @click="isExpanded = !isExpanded"
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
      <ThreadMessage
        :message="message"
        v-for="(message, index) in messages"
        :key="message.id"
        v-if="index === 0"
        :initiallyExpanded="true"
      ></ThreadMessage>
      <ThreadMessage
        :message="message"
        v-for="(message, index) in messages"
        :key="message.id"
        v-if="index > 0"
        :initiallyExpanded="false"
      ></ThreadMessage>
    </div>
  </div>
</template>

<script>
import ThreadMessage from '@/components/emails/ThreadMessage'
import Nylas from '@/services/nylas'

export default {
  name: 'Thread',
  components: { ThreadMessage },
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
      messages: {},
    }
  },
  created() {
    this.isExpanded = this.initiallyExpanded
    Nylas.getThreadMessages(this.thread.id).then(response => {
      this.messages = response.data
    })
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
