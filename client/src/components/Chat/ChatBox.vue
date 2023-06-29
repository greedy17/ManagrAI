<template>
  <section class="chat-container">
    <header class="title-header">
      <p style="margin-right: auto"><span>Latest: </span>{{ chatTitle }}</p>
      <!-- <div class="row pointer">
        <img style="margin-right:.5rem" src="@/assets/images/cloud.svg" height="18px" alt="" />
        sync
      </div>

      <div class="row pointer" @click="clearMessages">
        <img style="margin-right:.5rem" class="dampen" src="@/assets/images/cross-circle.svg" height="15px" alt="" />
        clear
      </div> -->
      <!-- <button class="small-button">
        <img class="dampen" src="@/assets/images/cloud.svg" height="16px" alt="" />
        sync
      </button> -->
      <button @click="clearMessages" class="small-button">
        <img class="dampen" src="@/assets/images/cross-circle.svg" height="12px" alt="" />
        Clear chat
      </button>
    </header>
    <div class="margin-top" ref="chatWindow">
      <div v-for="(message, i) in messages" :key="i" class="col-start">
        <div class="message-container">
          <div class="images">
            <span v-if="message.failed" style="font-size: 24px"> 🚫 </span>
            <span v-else-if="message.user === 'bot' && !message.updated" style="font-size: 24px">
              🤖
            </span>
            <span style="margin-left: -4px" v-else-if="message.user === 'bot' && message.updated">
              <img class="green-filter" src="@/assets/images/logo.png" height="30px" alt="" />
            </span>

            <div class="avatar" v-else>{{ userName[0] }}</div>
          </div>

          <div class="text-container">
            <div style="position: relative">
              <div
                class="type-header"
                :class="{ marg: message.gtMsg === 'AI Generated Summary' }"
                v-if="message.user === 'bot' && message.gtMsg"
              >
                <p>
                  {{ message.gtMsg }}
                </p>
                <small>
                  {{ message.data.Name }}
                </small>
              </div>

              <pre v-html="message.value" class="message-text"></pre>
            </div>

            <div v-if="message.generated">
              <div
                v-if="generating && generatingId === message.id"
                style="border-radius: 6px; padding: 0.2rem 0 0.25rem 0"
                class="row"
              >
                <!-- <p class="gray-text">Regenerating response</p> -->
                <div class="loading">
                  <div class="dot"></div>
                  <div class="dot"></div>
                  <div class="dot"></div>
                </div>
              </div>

              <div v-else style="margin-top: 1.5rem">
                <div class="column" v-if="message.generatedType === 'email' && addingInstructions">
                  <div class="space-between">
                    <small>Provide any additional instructions below:</small>

                    <p @click="closeInstructions">x</p>
                  </div>

                  <textarea
                    v-model="instructionText"
                    class="inline-input"
                    v-autoresize
                    autofocus="true"
                    rows="1"
                  />
                </div>

                <button
                  v-if="!addingInstructions"
                  style="margin-bottom: 0.25rem"
                  @click="
                    regenerate(
                      message.generatedType,
                      message.data['meeting_comments'],
                      message.id,
                      {
                        data: message.data,
                        integration: message.integrationId,
                        resource: message.resourceType,
                      },
                    )
                  "
                  class="content-button padding-small"
                >
                  <img
                    style="margin-right: 0.6rem"
                    class="gold-filter"
                    src="@/assets/images/sparkle.svg"
                    height="14px"
                    alt=""
                  />
                  Regenerate
                </button>

                <button
                  v-else
                  style="margin-bottom: 0.25rem"
                  @click="
                    regenerateEmail(instructionText, message.data['meeting_comments'], message.id)
                  "
                  class="content-button padding-small"
                >
                  <img
                    style="margin-right: 0.6rem"
                    class="gold-filter"
                    src="@/assets/images/sparkle.svg"
                    height="14px"
                    alt=""
                  />
                  Regenerate
                </button>

                <p v-if="message.error" style="margin-top: 0.5rem" class="red-text">
                  {{ message.error }}
                </p>
              </div>
            </div>
          </div>
        </div>

        <div
          v-if="message.user === 'bot' && message.formId && !message.updated"
          class="generate-container"
          style="margin-left: -0.5rem"
        >
          <button @click="toggleChatModal(message)" class="generate-button green">
            <img src="@/assets/images/wand.svg" class="invert" height="14px" alt="" />
            {{
              message.error
                ? 'Retry'
                : `Review & Update ${user.crm[0] + user.crm.slice(1).toLowerCase()}`
            }}
          </button>

          <p v-if="message.error" class="red-text">{{ message.error }}</p>
        </div>

        <div
          v-else-if="message.user === 'bot' && message.formId && message.updated"
          class="generate-container"
        >
          <div v-if="!message.generated">
            <button
              @click="toggleSelectContentOption(i)"
              v-if="!selectingContent || selectedIndex !== i"
              class="generate-button"
              style="margin-left: -0.75rem"
            >
              <img class="gold-filter" src="@/assets/images/sparkle.svg" height="16px" alt="" />
              Generate content
            </button>

            <div v-else-if="selectingContent && selectedIndex === i">
              <div
                style="position: relative; margin-bottom: 2rem; margin-left: -0.75rem"
                class="row"
                v-if="!generating"
              >
                <button
                  @click="generateEmail(message.data['meeting_comments'], message.id)"
                  class="content-button"
                >
                  <font-awesome-icon icon="fa-regular fa-envelope" />Draft follow-up email

                  {{ message.note }}
                </button>
                <button
                  @click="nextSteps(message.data['meeting_comments'], message.id)"
                  class="content-button"
                >
                  <font-awesome-icon style="height: 10px" icon="fa-solid fa-angles-right" />
                  Suggest next steps
                </button>
                <button
                  @click="
                    getSummary(
                      message.data,
                      message.integrationId,
                      message.resourceType,
                      message.id,
                    )
                  "
                  class="content-button"
                >
                  <font-awesome-icon icon="fa-regular fa-file-lines" />Get summary
                </button>

                <img
                  style="margin-left: 0.25rem; cursor: pointer"
                  class="gray-blue-scale"
                  @click="selectingContent = !selectingContent"
                  src="@/assets/images/return.svg"
                  height="18px"
                  alt=""
                />
              </div>

              <div v-else class="loader-container">
                <span
                  style="
                    font-size: 20px;
                    margin-right: .75rem;
                    padding-top: 0.75rem;
                    margin-left: -2.75rem
                    margin-top: 0.5rem;
                  "
                  >🚀</span
                >

                <div style="border-radius: 6px; padding: 0.25rem 0.25rem" class="row">
                  <p>Processing your submission</p>
                  <div class="loading">
                    <div class="dot"></div>
                    <div class="dot"></div>
                    <div class="dot"></div>
                  </div>
                </div>
              </div>
            </div>

            <p class="red-text" v-if="message.error">{{ message.error }}</p>
          </div>
        </div>
      </div>

      <div style="margin-left: 1rem" v-show="messageLoading" class="loader-container">
        <span
          style="font-size: 20px; margin-right: 0.5rem; padding-top: 0.75rem; margin-left: 0.25rem"
          >🚀</span
        >

        <div style="border-radius: 6px; padding: 0.25rem 0.75rem" class="row">
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
import User from '@/services/users'

export default {
  name: 'ChatBox',
  components: {
    ChatTextBox,
  },
  data() {
    return {
      selectingContent: false,
      messageLoading: false,
      generating: false,
      selectedIndex: null,
      generativeRes: null,
      generatingId: null,
      addingInstructions: false,
      instructionText: null,
    }
  },
  watch: {
    messages: 'scrollToBottom',
  },
  methods: {
    regenerate(type, data, editId, sumObj) {
      this.generatingId = editId
      if (type === 'email') {
        this.addingInstructions = true
      } else if (type === 'next') {
        this.regenerateNext(data, editId)
      } else {
        this.regenerateSummary(editId, sumObj)
      }
    },
    closeInstructions() {
      this.addingInstructions = false
      this.instructionText = null
    },
    clearMessages() {
      this.$store.dispatch('clearMessages')
    },
    async regenerateEmail(instructions, note, editId) {
      this.generating = true
      try {
        let res = await User.api.chatEmail({
          id: this.user.id,
          notes: note,
          instructions: instructions,
        })
        this.generativeRes = res
        this.$store.dispatch('editMessages', {
          id: editId,
          value: this.generativeRes['res'],
        })
      } catch (e) {
        console.log(e)
        this.$store.dispatch('messageUpdateFailed', { id: editId, data: e.data.error })
      } finally {
        this.instructionText = null
        this.generating = false
        this.addingInstructions = false
      }
    },
    async regenerateNext(note, editId) {
      this.generating = true
      try {
        let res = await User.api.chatNextSteps({
          id: this.user.id,
          notes: note,
        })
        this.generativeRes = res
        this.$store.dispatch('editMessages', {
          id: editId,
          value: this.generativeRes['res'],
        })
      } catch (e) {
        console.log(e)
        this.$store.dispatch('messageUpdateFailed', { id: editId, data: e.data.error })
      } finally {
        this.generating = false
      }
    },
    async regenerateSummary(editId, sumObj) {
      this.generating = true
      try {
        let res = await User.api.getSummary({
          id: this.user.id,
          data: sumObj.data,
          integrationId: sumObj.integration,
          resource: sumObj.resource,
        })
        this.generativeRes = res
        this.$store.dispatch('editMessages', {
          id: editId,
          value: this.generativeRes['res'],
        })
      } catch (e) {
        console.log(e)
        this.$store.dispatch('messageUpdateFailed', { id: editId, data: e.data.error })
      } finally {
        this.generating = false
      }
    },
    async generateEmail(note, id) {
      this.generating = true
      try {
        let res = await User.api.chatEmail({
          id: this.user.id,
          notes: note,
          instructions: null,
        })
        this.generativeRes = res
        this.$store.dispatch('editMessages', {
          user: 'bot',
          id: id,
          value: this.generativeRes['res'],
          gtMsg: 'AI Generated Email',
          generated: true,
          generatedType: 'email',
        })
      } catch (e) {
        console.log(e)
        this.$store.dispatch('messageUpdateFailed', { id: id, data: e.data.error })
      } finally {
        this.generating = false
      }
    },
    async nextSteps(note, id) {
      this.generating = true
      try {
        let res = await User.api.chatNextSteps({
          id: this.user.id,
          notes: note,
        })
        this.generativeRes = res
        this.$store.dispatch('editMessages', {
          user: 'bot',
          id: id,
          value: this.generativeRes['res'],
          gtMsg: 'AI Generated Next Steps',
          generated: true,
          generatedType: 'next',
        })
      } catch (e) {
        console.log(e)
        this.$store.dispatch('messageUpdateFailed', { id: id, data: e.data.error })
      } finally {
        this.generating = false
      }
    },

    async getSummary(data, id, resource, msgId) {
      this.generating = true
      try {
        let res = await User.api.getSummary({
          id: this.user.id,
          data: data,
          integrationId: id,
          resource: resource,
        })
        this.generativeRes = res
        this.$store.dispatch('editMessages', {
          user: 'bot',
          id: msgId,
          value: this.generativeRes['res'],
          gtMsg: 'AI Generated Summary',
          generated: true,
          generatedType: 'summary',
        })
      } catch (e) {
        console.log(e)
        this.$store.dispatch('messageUpdateFailed', { id: id, data: e.data.error })
      } finally {
        this.generating = false
      }
    },
    toggleSelectContentOption(i) {
      if (i) {
        this.selectedIndex = i
      }
      this.selectingContent = !this.selectingContent
      this.scrollToBottom()
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
      this.$emit('set-opp', data.resource)
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
  directives: {
    autoresize: {
      inserted(el) {
        function adjustTextareaHeight() {
          el.style.height = 'auto'
          el.style.height = el.scrollHeight + 'px'
        }

        el.addEventListener('input', adjustTextareaHeight)
        el.addEventListener('focus', adjustTextareaHeight)
        adjustTextareaHeight()
      },
    },
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
.dampen {
  filter: invert(45%);
  margin-left: 1rem;
}

.red-text {
  color: $coral;
}

.gray-text {
  color: $light-gray-blue;
}

.marg {
  margin-bottom: 0 !important;
}

.type-header {
  position: sticky;
  top: 0;
  left: 0;
  margin-bottom: -2rem;

  p {
    font-size: 13px;
  }
  small {
    color: $light-gray-blue;
  }
}

.message-text {
  font-family: $base-font-family;
  word-wrap: break-word;
  white-space: pre-wrap;
  padding: 0;
  margin: 0;
}

.gray-blue-scale {
  filter: invert(82%) sepia(2%) saturate(5238%) hue-rotate(201deg) brightness(78%) contrast(75%);
}

.padding-small {
  padding: 0.5rem 0.75rem !important;
}

.row {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-start;
}

.column {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  padding-top: 1rem;
}

.space-between {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  width: 100%;

  p {
    margin-top: 0;
    margin-right: 0.25rem !important;
    border: 1px solid rgba(0, 0, 0, 0.1);
    padding: 0 6px !important;
    border-radius: 4px;
    cursor: pointer;
  }
}

.inline-input {
  outline: none;
  padding: 0.5rem 0.75rem;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 6px;
  color: $base-gray;
  width: 100%;
  font-family: $base-font-family;
  font-size: 12px;
  line-height: 1.5;
  letter-spacing: 0.4px;
  resize: none;
  margin: 0.75rem 0;
}

.chat-container {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  padding-bottom: 1rem;
  // padding: 1rem 1.5rem;
  font-size: 14px;
  position: relative;
}

.offwhite-bg {
  background-color: white !important;
}

.message-container {
  display: flex;
  align-items: flex-start;
  justify-content: flex-start;
  margin: 0;
  width: 100%;
  padding: 0 1.5rem;

  p {
    padding: 0;
    margin: 0;
  }

  &:hover {
    background-color: $off-white !important;
  }
}

.message-container:first-of-type {
  padding-top: 0.5rem;
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
  overflow: scroll;
  background-color: white;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 6px;
  padding: 0 0.75rem;
  line-height: 1.75;
  position: relative;

  &:hover {
    background-color: $off-white !important;
  }
}

.text-container {
  overflow: scroll;
  padding: 0.25rem;
  margin: 0;
  line-height: 1.75;
}

.images {
  padding: 0;
  margin: 0 0.5rem 0 0;
}

.bottom {
  position: sticky;
  bottom: 0;
  left: 0;
}

.bottom-right {
  position: absolute;
  bottom: 0;
  right: 0;
}

.avatar {
  background-color: $purple;
  color: white;
  width: 22px;
  height: 22px;
  margin-right: 0.2rem;
  margin-top: 6px;
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
  padding: 0.75rem 1rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: flex-end;
  font-family: $base-font-family;
  background-color: white;

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

    span {
      color: $light-gray-blue;
    }
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
  padding: 0 1rem 0.5rem 4.5rem;
  background-color: white;
  width: 100%;
}

.generate-button {
  @include chat-button();
  padding: 0.6rem 0.8rem;
  margin-bottom: 0.5rem;
  img {
    margin-right: 0.5rem;
  }
}

.content-button {
  @include chat-button();
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  margin-right: 0.5rem;
  svg {
    margin-right: 0.5rem;
  }
}

.small-button {
  @include chat-button();
  border: 1px solid rgba(0, 0, 0, 0.1);
  background-color: transparent;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  border-radius: 5px;
  font-size: 12px;
  padding: 0.35rem;
  margin-left: 1rem;
  font-weight: normal;

  img {
    margin: 0;
    margin-right: 0.5rem;
  }
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

.pointer {
  cursor: pointer;
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