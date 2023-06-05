<template>
  <section class="chat-container">
    <header class="title-header">
      <p @click="clearMessages">{{ chatTitle }}</p>
    </header>
    <div class="margin-top" ref="chatWindow">
      <div v-for="(message, i) in messages" :key="i" class="col-start">
        <div class="message-container">
          <div class="images">
            <span
              v-if="message.user === 'bot' && !message.updated"
              style="font-size: 24px; margin-right: 0.25rem; padding-top: 0.5rem"
            >
              🤖
            </span>
            <span v-else-if="message.user === 'bot' && message.updated">
              <img class="green-filter" src="@/assets/images/logo.png" height="30px" alt="" />
            </span>

            <div class="avatar" v-else>{{ userName[0] }}</div>
          </div>

          <div :class="message.user === 'bot' ? 'ai-text-container' : 'text-container'">
            <p>{{ message.value }}</p>
          </div>
        </div>

        <div
          v-if="message.user === 'bot' && message.formId && !message.updated"
          class="generate-container"
        >
          <button @click="toggleChatModal(message)" class="generate-button green">
            <img src="@/assets/images/wand.svg" class="invert" height="14px" alt="" />
            {{ `Review & update ${user.crm.toLowerCase()}` }}
          </button>
        </div>

        <div
          v-else-if="message.user === 'bot' && message.formId && message.updated"
          class="generate-container"
        >
          <button
            @click="toggleSelectContentOption(i)"
            v-if="!selectingContent || selectedIndex !== i"
            class="generate-button"
          >
            <img class="gold-filter" src="@/assets/images/sparkle.svg" height="16px" alt="" />
            Generate content
          </button>

          <div
            style="position: relative; margin-bottom: 0.5rem"
            class="row"
            v-else-if="selectingContent && selectedIndex === i"
          >
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

            <img
              style="margin-left: 0.25rem; cursor: pointer"
              class="gray-blue-scale"
              @click="selectingContent = !selectingContent"
              src="@/assets/images/return.svg"
              height="18px"
              alt=""
            />

            <!-- <div @click="selectingContent = !selectingContent" class="go-back">
              <div class="back">
                <p>X</p>
               
              </div>
            </div> -->
          </div>
        </div>
      </div>

      <div v-show="messageLoading" class="loader-container">
        <span
          style="font-size: 20px; margin-right: 1.1rem; padding-top: 0.5rem; margin-left: 0.25rem"
          >🚀</span
        >

        <div
          style="background-color: #eeeeee; border-radius: 6px; padding: 0.25rem 0.75rem"
          class="row"
        >
          <p>Processing your submission</p>
          <div class="loading">
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
          </div>
        </div>
      </div>

      <!-- <div>{{ user.salesforceAccountRef }}</div> -->
    </div>

    <ChatTextBox
      class="bottom"
      @message-loading="setLoader"
      @set-message="setMessage"
      @set-title="setTitle"
      :messages="messages"
      :scrollToBottom="scrollToBottom"
    />
  </section>
</template>
  
<script>
import ChatTextBox from './ChatTextBox.vue'
import SlackOAuth from '@/services/slack'

export default {
  name: 'ChatBox',
  components: {
    ChatTextBox,
  },
  data() {
    return {
      selectingContent: false,
      messageLoading: false,
      selectedIndex: null,
    }
  },
  methods: {
    clearMessages() {
      this.$store.dispatch('clearMessages')
    },
    // async getAllCustomSlackForms() {
    //   try {
    //     let res = await SlackOAuth.api.slackFormInstances()
    //     console.log(res)
    //   } catch (e) {
    //     console.log(e)
    //   } finally {
    //   }
    // },
    toggleSelectContentOption(i) {
      if (i) {
        this.selectedIndex = i
      }
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
    setMessage(msg) {
      this.$store.dispatch('updateMessages', msg)
    },
    setTitle(title) {
      this.$store.dispatch('updateChatTitle', title)
    },
    toggleChatModal(data) {
      this.$emit('toggle-chat-modal', data)
    },
  },
  computed: {
    user() {
      return this.$store.state.user
    },
    userName() {
      return this.$store.state.user.firstName
    },
    chatTitle() {
      return this.$store.state.chatTitle
    },
    messages() {
      return this.$store.state.messages
    },
  },
  created() {
    this.scrollToBottom()
  },
  // beforeRouteLeave() {
  //   this.$store.dispatch('updateChatTitle', 'All Open Opportunities')
  // },
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
.gray-blue-scale {
  filter: invert(82%) sepia(2%) saturate(5238%) hue-rotate(201deg) brightness(78%) contrast(75%);
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
.gold-filter {
  filter: invert(89%) sepia(43%) saturate(4130%) hue-rotate(323deg) brightness(90%) contrast(87%);
  animation: shimmer 2s;
  -webkit-mask: linear-gradient(-60deg, #000 30%, #0005, #000 70%) right/200% 100%;
}

.invert {
  filter: invert(95%);
}

.green {
  background-color: $dark-green !important;
  color: white !important;
  border: 1px solid $dark-green !important;
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
  width: 4px;
  height: 4px;
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
  // background-color: $dark-green;
  // border: 1px solid $dark-green;
  // color: $dark-green;
  margin-bottom: 0.5rem;

  img {
    margin-right: 0.5rem;
    // filter: invert(87%) sepia(25%) saturate(6867%) hue-rotate(2deg) brightness(107%) contrast(103%);
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

.go-back {
  position: absolute;
  right: 0.5rem;
  top: -1.75rem;
  display: flex;
  flex-direction: row;
  align-items: center;
}

.back {
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  outline: 1px solid rgba(0, 0, 0, 0.1);
  color: $coral;
  width: 20px;
  height: 20px;
  border-radius: 3px;
  cursor: pointer;
  margin-left: 0.5rem;
  margin-right: 2px;
  font-size: 11px;
  transition: all 0.3s;

  &:hover {
    box-shadow: 0 3px 6px 0 $very-light-gray;
    scale: 1.025;
  }

  img {
    transform: rotate(180deg);
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