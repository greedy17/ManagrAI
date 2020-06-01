<template>
  <div class="actions__item" style="width: 80%">
    <div class="actions__row">
      <div class="actions__item-header-icon">
        <img
          alt="icon"
          :src="require(`@/assets/images/email.svg`)"
          @click="isExpanded = !isExpanded"
          :class="{ 'filter-green': isExpanded }"
          class="icon"
        />
      </div>

      <div class="actions__item-header-title">
        {{ message.subject }}<br /><em v-if="!isExpanded">{{ message.snippet }}</em>
      </div>
      <div class="actions__item-header-date" v-if="!isExpanded">
        From:
        <div v-for="contact in message.from" class="email__contact-tag">{{ contact.email }}</div>
      </div>
      <div class="actions__item-header-date" v-if="!isExpanded">
        To:
        <div v-for="contact in message.to" class="email__contact-tag">{{ contact.email }}</div>
      </div>
    </div>
    <div class="email__row" v-if="isExpanded">
      <div class="email__row">
        {{ message.date | momentDateTimeShort }}
      </div>
      <div class="email__row">
        From:
        <div v-for="contact in message.from" class="email__contact-tag">{{ contact.email }}</div>
      </div>
      <div class="email__row">
        To:
        <div v-for="contact in message.to" class="email__contact-tag">{{ contact.email }}</div>
      </div>
    </div>
    <div style="width: 100%" v-if="isExpanded">
      <div style="width: 100%" v-html="message.body"></div>
    </div>
    <div style="width: 100%" v-if="isExpanded">
      <div class="box" v-if="isExpanded"></div>
      <EmailCompose
        @emailSent="emailSent"
        :reply-message="message"
        :show-subject="false"
      ></EmailCompose>
    </div>
  </div>
</template>

<script>
import EmailCompose from '@/components/emails/EmailCompose'

export default {
  name: 'message',
  components: { EmailCompose },
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
  },
  data() {
    return {
      isExpanded: false,
    }
  },
  created() {
    this.isExpanded = this.initiallyExpanded
  },
  methods: {
    emailSent() {
      this.$emit('emailSent')
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/layout';
@import '@/styles/containers';
@import '@/styles/forms';
.filter-green {
  filter: invert(45%) sepia(96%) saturate(2978%) hue-rotate(123deg) brightness(92%) contrast(80%);
}
</style>
