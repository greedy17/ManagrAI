<template>
  <section class="chat-container">
    <div v-for="message in messages" :key="message.id">
      <div class="message-container">
        <div class="images">
          <img v-if="message.user === 'bot'" src="@/assets/images/logo.png" height="30px" />
          <div class="avatar" v-else>{{ userName[0] }}</div>
        </div>

        <div :class="message.user === 'bot' ? 'ai-text-container' : 'text-container'">
          <p>{{ message.value }}</p>
        </div>
      </div>
    </div>

    <ChatTextBox class="bottom" :messages="messages" />
  </section>
</template>
  
<script>
import ChatTextBox from './ChatTextBox.vue'

export default {
  name: 'ChatBox',
  components: {
    ChatTextBox,
  },
  data() {
    return {
      // user: { },
      messages: [
        // { id: 0, value: "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.", user: '1' },
        {
          id: 0,
          user: 'bot',
          value: `Hey ${
            this.userName ? this.userName : 'there'
          }! Welcome to Managr, your AI sales assistant.\n\nYou are currently in our Playground environment. Whenever you're ready, please go and connect your CRM along with the rest of your apps.\n\n- To get started, type in an easy command like, "update Opportunity Pied Piper, move close date to the end of the month" below.`,
        },
        {
          id: 1,
          value: 'Update Opportunity Pied Piper, move close date to the end of June.',
          user: 1,
        },
        { id: 2, value: 'Successfully updated Pied Piper', user: 'bot' },
      ],
    }
  },
  methods: {},
  computed: {
    userName() {
      return this.$store.state.user.firstName
    },
  },
  created() {},
}
</script>
  
<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';
@import '@/styles/cards';
@import '@/styles/mixins/utils';
@import '@/styles/mixins/inputs';

.chat-container {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  padding: 1rem 1.5rem;
  font-size: 16px;
  position: relative;
}
.message-container {
  display: flex;
  align-items: flex-start;
  justify-content: flex-start;
  margin: 1rem 0rem;

  p {
    padding: 0;
    margin: 0;
  }
}
.container-padding {
  border-radius: 6px;
  padding: 0.5rem;
}

.ai-text-container {
  background-color: $soft-gray;
  border-radius: 6px;
  padding: 1.25rem 0.75rem;
}

.text-container {
  padding: 0 0.5rem;
  margin: 0;
}

.images {
  padding: 0;
  margin: 0 1rem 0 0;
}

.bottom {
  position: absolute;
  bottom: 0;
  left: 0;
}

.avatar {
  background-color: $purple;
  color: white;
  width: 30px;
  height: 30px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
}

@media (max-width: 768px) {
  .chat-container {
    font-size: 14px;
  }
}
</style>