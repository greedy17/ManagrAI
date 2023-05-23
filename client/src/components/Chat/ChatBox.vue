<template>
  <section class="chat-container">
    <header class="title-header"><p>All Open Opportunities</p></header>
    <div class="margin-top" ref="chatWindow">
      <div v-for="(message, i) in messages" :key="i" class="col-start">
        <div class="message-container">
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

        <div v-if="message.user === 'bot' && i !== 0" class="generate-container">
          <button
            @click="toggleSelectContentOption"
            v-if="!selectingContent"
            class="generate-button"
          >
            <img src="@/assets/images/sparkle.svg" height="16px" alt="" /> Generate content
          </button>

          <div class="row" v-else>
            <button class="content-button">
              <font-awesome-icon @click="selectedOpp = null" icon="fa-regular fa-envelope" />Draft
              follow-up email
            </button>
            <button class="content-button">
              <font-awesome-icon
                style="height: 10px"
                @click="selectedOpp = null"
                icon="fa-solid fa-angles-right"
              />
              Suggest next steps
            </button>
            <button class="content-button">
              <font-awesome-icon @click="selectedOpp = null" icon="fa-regular fa-file-lines" />Get
              summary
            </button>
          </div>
        </div>
      </div>

      <div v-show="messageLoading" class="loader-container">
        <img
          class="green-filter"
          style="margin-right: 1rem"
          src="@/assets/images/logo.png"
          height="30px"
        />

        <div class="loading">
          <div class="dot"></div>
          <div class="dot"></div>
          <div class="dot"></div>
        </div>
      </div>

      <!-- <div>{{ user.salesforceAccountRef }}</div> -->
    </div>

    <ChatTextBox
      class="bottom"
      @message-loading="setLoader"
      :messages="messages"
      :scrollToBottom="scrollToBottom"
    />
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
      selectingContent: false,
      messageLoading: false,
      messages: [
        // { id: 0, value: "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.", user: '1' },
        {
          id: 0,
          user: 'bot',
          value: `Hey ${
            this.userName ? this.userName : 'there'
          }! Welcome to Managr, your AI sales assistant`,
        },
        // {
        //   id: 1,
        //   value: 'Update Opportunity Pied Piper, move close date to the end of June.',
        //   user: 1,
        // },
        // { id: 2, value: 'Successfully updated Pied Piper', user: 'bot' },
      ],
    }
  },
  methods: {
    toggleSelectContentOption() {
      this.selectingContent = !this.selectingContent
    },
    scrollToBottom() {
      setTimeout(() => {
        const chatWindow = this.$refs.chatWindow
        chatWindow.scrollTop = chatWindow.scrollHeight
      }, 0)
    },
    setLoader(val) {
      this.messageLoading = val
    },
  },
  computed: {
    user() {
      return this.$store.state.user
    },
    userName() {
      return this.$store.state.user.firstName
    },
  },

  created() {
    this.scrollToBottom()
  },
}
</script>
  
<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';
@import '@/styles/cards';
@import '@/styles/mixins/utils';
@import '@/styles/mixins/inputs';

@keyframes shimmer {
  100% {
    -webkit-mask-position: left;
  }
}

.row {
  display: flex;
  justify-content: row;
  align-items: center;
  justify-content: flex-start;
}

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
// .margin-top:hover {
//   overflow-y: auto;
//   scroll-behavior: smooth;
// }

// .margin-top::-webkit-scrollbar {
//   width: 6px;
//   height: 0px;
//   margin-left: 0.25rem;
// }
// .margin-top::-webkit-scrollbar-thumb {
//   background-color: $base-gray;
//   box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
//   border-radius: 6px;
// }
.container-padding {
  border-radius: 6px;
  padding: 0.5rem;
}

.ai-text-container {
  background-color: $soft-gray;
  border-radius: 6px;
  padding: 0.5rem 0.75rem;
  line-height: 1.75;
  position: relative;
}

.text-container {
  padding: 0 0.5rem;
  margin: 0;
  line-height: 1.75;
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

.loader-container {
  display: flex;
  align-items: flex-start;
  justify-content: flex-start;
  margin-bottom: 1.5rem;
}

.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  // background-color: $soft-gray;
  border-radius: 6px;
  padding: 0.75rem 0.75rem;
}

.dot {
  width: 6px;
  height: 6px;
  margin: 0 5px;
  background: rgb(97, 96, 96);
  border-radius: 50%;
  animation: bounce 1.2s infinite ease-in-out;
}

.dot:nth-child(2) {
  animation-delay: -0.4s;
}

.dot:nth-child(3) {
  animation-delay: -0.2s;
}

.col-start {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.generate-container {
  padding: 0.5rem 2.75rem;
  margin-top: -1.25rem;
}

.generate-button {
  @include chat-button();
  padding: 0.7rem 0.8rem;
  background-color: $dark-green;
  color: white;
  border: none;
  margin-bottom: 0.5rem;

  img {
    margin-right: 0.5rem;
    filter: invert(87%) sepia(25%) saturate(6867%) hue-rotate(2deg) brightness(107%) contrast(103%);
    // animation: shimmer 2s infinite;
    // -webkit-mask: linear-gradient(-60deg, #000 30%, #0005, #000 70%) right/200% 100%;
  }
}

.content-button {
  @include chat-button();
  margin-right: 0.5rem;
  svg {
    margin-right: 0.5rem;
  }
  // img {
  //   margin-right: 0.5rem;
  //   animation: shimmer 2s infinite;
  //   -webkit-mask: linear-gradient(-60deg, #000 30%, #0005, #000 70%) right/200% 100%;
  // }
}

@keyframes bounce {
  0%,
  80%,
  100% {
    transform: scale(0);
    opacity: 0;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

// @keyframes typing {
//   from {
//     width: 0;
//   }
//   to {
//     width: 100%;
//   }
// }

// @keyframes blinking {
//   0% {
//     border-right-color: transparent;
//   }
//   50% {
//     border-right-color: rgb(66, 65, 65);
//   }
//   100% {
//     border-right-color: transparent;
//   }
// }

// .typed {
//   overflow: hidden;
//   white-space: nowrap;
//   width: 0;
//   animation: typing 1.5s steps(30, end) forwards, blinking 1s infinite;
//   border-right: 1px solid;
// }
</style>