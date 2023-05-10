<template>
  <section class="input-section">
    <div class="input-container">
      <font-awesome-icon style="height: 20px; width: 20px" icon="fa-regular fa-square-plus" />
      <input v-on:keyup.enter="sendMessage" class="input" placeholder="Start typing here..." v-model="message" />
      <font-awesome-icon icon="fa-regular fa-paper-plane" @click="sendMessage" />
    </div>
  </section>
</template>

<script>
export default {
  name: 'ChatTextBox',
  components: {},
  props: {
    messages: {
      type: Array
    }
  },
  data() {
    return {
      message: '',
    }
  },
  methods: {
    sendMessage() {
      try {
        const newId = Math.ceil(Math.random() * 10000)
        const newMessage = {
          id: newId,
          value: this.message,
          user: 1,
        }
        const originalMessage = this.message
        this.messages.push(newMessage)
        this.message = ''
        setTimeout(() => {
          const botMessage = {
            id: newId+1,
            value: '...',
            user: 'bot',
          }
          this.messages.push(botMessage)
          setTimeout(() => {
            const newBotMessage = this.messages.pop()
            if (originalMessage === 'I always feel like...') {
              newBotMessage.value = `Somebody's watching me!`
            } else {
              newBotMessage.value = `Bot message!`
            }
            this.messages.push(newBotMessage)
          }, 2000)
        }, 500)
      } catch (e) {
        console.log('Error in sendMessage: ', e)
      }
    },
  },
  computed: {},
  created() {},
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';
@import '@/styles/cards';
@import '@/styles/mixins/utils';
@import '@/styles/mixins/inputs';
.input-section {
  display: flex;
  align-items: center;
  padding: 1rem 1.5rem;
  width: 100%;
  background-color: $off-white;
}

.input-container {
  display: flex;
  align-items: center;
  flex-wrap: nowrap;
  border: 1px solid rgba(0, 0, 0, 0.1);
  padding: 0 1rem;
  border-radius: 6px;
  width: 100%;
  background-color: white;
}

.input {
  width: 95%;
  outline: none;
  border: none;
  padding: 1rem;
}
</style>