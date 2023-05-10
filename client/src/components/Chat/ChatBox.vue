<template>
  <section class="chat-container">
    <div class="messages-container">
      <div v-for="message in messages" :key="message.id">
        <div class="message-container">
          <div class="profile-pic">
            <img v-if="message.user === 'bot'" src="@/assets/images/logo.png" height="30px" />
            <img v-else src="@/assets/images/person.svg" height="30px" />
          </div>
          <div class="container-padding" :class="message.user === 'bot' ? 'ai-text-container' : 'text-container'">
            <p>{{ message.value }}</p>
          </div>
        </div>
      </div>
    </div>
    <ChatTextBox />
  </section>
</template>
  
<script>
  import ChatTextBox from './ChatTextBox.vue';

  export default {
    name: 'ChatBox',
    components: {
      ChatTextBox
    },
    data() {
      return {
        // user: { },
        messages: [
          // { id: 0, value: "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.", user: '1' },
          { id: 0, user: 'bot', value: `Hey ${this.userName ? this.userName : 'there'}! Welcome to Managr, your AI sales assistant.\n\nYou are currently in our Playground environment. Whenever you're ready, please go and connect your CRM along with the rest of your apps.\n\n- To get started, type in an easy command like, "update Opportunity Pied Piper, move close date to the end of the month" below.` },
          { id: 1, value: "Update Opportunity Pied Piper, move close date to the end of June.", user: 1 },
          { id: 2, value: "Successfully updated Pied Piper", user: 'bot' },
        ],
      }
    },
    methods: {

    },
    computed: {
      userName() {
        return this.$store.state.user.firstName
      },
    },
    created() {

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
    // width: 70vw;
    // border: 1px solid $very-light-gray;
    display: flex;
    flex-direction: column;
    width: 100%;
    height:100%;
    padding: 2.5rem .5rem;
  }
  .message-container {
    display: flex;
  }
  .messages-container {
    height: 75vh;
  }
  .text-container {

  }
  .profile-pic {
    display: flex;
    align-items: center;
    margin: auto 10px;
  }
  .container-padding {
    padding: 0.5rem;
    margin-bottom: 0.5rem;
    border-radius: 4px;
  }
  .ai-text-container {
    background-color: $soft-gray;
  }
</style>