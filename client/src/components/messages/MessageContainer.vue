<template>
  <div class="messages-container">
    <div class="direction">
      <h4>{{ direction }}</h4>
    </div>
    <div class="messages">
      <div v-if="messages.length < 1" class="muted">No Messages {{ direction }}</div>
      <div :key="message.sid" v-for="message in messages">
        <Message :message="message" />
        <div class="divider"></div>
      </div>
    </div>
  </div>
</template>

<script>
/**
 *
 * Special Component for Twilio Messages
 */
import Message from '@/components/messages/_Message'
export default {
  name: 'MessagesContainer',
  components: {
    Message,
  },
  props: {
    messages: {
      type: Array,
      required: true,
    },
    direction: {
      type: String,
      required: true,
    },
  },
  data() {
    return {}
  },
  created() {},
  computed: {},
  methods: {},
}
</script>

<style lang="scss" scoped>
@import '@/styles/layout';
@import '@/styles/containers';
@import '@/styles/forms';
@import '@/styles/variables';

ul {
  list-style-type: none;
}
.messages-container {
  padding: 1rem 1rem;
  display: flex;

  border-radius: 5px;
  flex-direction: column;
  height: 30rem;
  overflow-y: scroll;
  box-shadow: 0px 0px 8px 2px $off-white inset;
  .direction {
    position: sticky;
    position: -webkit-sticky;
    padding: 0 1rem;
    top: 0;
    background-color: white;
    box-shadow: 0px -5px 10px 10px $off-white;
  }

  .messages {
    margin-top: 1rem;
    padding: 0 1rem;
  }

  .divider {
    width: 100%;
    border-bottom: 2px solid $off-white;
  }
}
</style>
