<template>
  <section class="chat-container">
    <header class="title-header"><p>All Open Opportunities</p></header>
    <div class="margin-top">
      <div v-for="message in messages" :key="message.id" class="message-container">
        <div class="images">
          <img
            class="green-filter"
            v-if="message.user === 'bot'"
            src="@/assets/images/logo.png"
            height="30px"
          />

          <div class="avatar" v-else>{{ userName[0] }}</div>
        </div>

        <div :class="message.user === 'bot' ? 'ai-text-container' : 'text-container'">
          <p>{{ message.value }}</p>
        </div>
      </div>
    </div>

    <ChatTextBox class="bottom" :messages="messages" />
    <!-- :scrollToBottom="scrollToBottom"  -->
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
  methods: {
    // scrollToBottom() {
    //   const chatWindow = this.$refs.chatWindow
    //   chatWindow.scrollTop = chatWindow.scrollHeight
    // },
  },
  computed: {
    userName() {
      return this.$store.state.user.firstName
    },
  },
  created() {
    // this.scrollToBottom()
  },
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
  // height: 100vh;
  padding: 1rem 1.5rem;
  font-size: 14px;
  position: relative;
}

.message-container {
  display: flex;
  align-items: flex-start;
  justify-content: flex-start;
  margin-bottom: 1.5rem;

  p {
    padding: 0;
    margin: 0;
  }
}
.margin-top {
  margin-top: 4rem;
  height: 96%;
  overflow-y: scroll;
}
.container-padding {
  border-radius: 6px;
  padding: 0.5rem;
}

.ai-text-container {
  background-color: $soft-gray;
  border-radius: 6px;
  padding: 1rem 0.75rem;
  line-height: 1.75;
}

.text-container {
  padding: 0 0.5rem;
  margin: 0;
  line-height: 1.5;
}

.images {
  padding: 0;
  margin: 0 1rem 0 0;
}

.bottom {
  position: sticky;
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

.title-header {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  padding: 1rem 0rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: $base-font-family;
  background-color: $off-white;

  h4,
  p {
    margin: 0;
    padding: 0.5rem;
    width: fit-content;
    // outline: 1px solid rgba(0, 0, 0, 0.1);
    border-radius: 6px;
    // background-color: white;
    font-size: 12px;
    letter-spacing: 0.4px;
  }
}

@media (max-width: 768px) {
  .chat-container {
    font-size: 14px;
  }
}

.green-filter {
  filter: brightness(0%) invert(64%) sepia(8%) saturate(2746%) hue-rotate(101deg) brightness(97%)
    contrast(82%);
}
</style>