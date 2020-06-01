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
      <div class="actions__item-header-title">{{ message.subject }}</div>
      <div class="actions__item-header-date" v-if="!isExpanded">
        <span class="thread-message-email">From: {{ message.from[0].name }}</span>
      </div>
      <div class="actions__item-header-date">
        <span class="thread-message-email">To: {{ message.to[0].name }}</span>
      </div>
    </div>
    <div class="actions__item-header" v-if="isExpanded">
      <div class="actions__item-header-date">
        <span class="thread-message-email">From: {{ message.from[0].name }}</span>
      </div>
      <div class="actions__item-header-date">
        <span class="thread-message-email">To: {{ message.to[0].name }}</span>
      </div>
    </div>
    <div class="actions__item-header" v-if="isExpanded">
      <div v-html="message.body"></div>
    </div>
    <div class="action__items-header" v-if="isExpanded">
      <div class="box" v-if="isExpanded"></div>
      <div class="box__tab-header">
        <div
          class="box__tab"
          @click="toggleActiveTab('reply')"
          :class="{ 'box__tab--active': replyActive }"
        >
          Reply
        </div>
        <div
          class="box__tab"
          @click="toggleActiveTab('replyAll')"
          :class="{ 'box__tab--active': replyAllActive }"
        >
          Reply All
        </div>
      </div>
      <div class="box__content">
        <textarea name="test" id="" rows="10" style="width: 100%"></textarea>
        <button class="button">Send</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'message',
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
      replyActive: false,
      replyAllActive: true,
      isExpanded: false,
    }
  },
  created() {
    this.isExpanded = this.initiallyExpanded
  },
  methods: {
    toggleActiveTab(tabToActivate) {
      this.replyActive = false
      this.replyAllActive = false
      if (tabToActivate === 'reply') this.replyActive = true
      if (tabToActivate === 'replyAll') this.replyAllActive = true
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
