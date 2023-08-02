<template>
  <section class="chat-container">
    <header class="title-header">
      <p style="margin-right: auto"><span>Latest: </span>{{ chatTitle }}</p>
      <button @click="deleteMessages" class="small-button">
        <img class="dampen" src="@/assets/images/cross-circle.svg" height="12px" alt="" />
        Clear chat
      </button>
    </header>
    <div class="margin-top" ref="chatWindow">
      <div class="col-start">
        <div class="message-container">
          <div class="images">
            <span style="margin-left: -4px" v-if="toggleReady">
              <img class="green-filter" src="@/assets/images/logo.png" height="30px" alt="" />
            </span>
            <span style="font-size: 24px" v-else> 🤖 </span>
          </div>
          <div class="text-container">
            <div style="position: relative">
              <!-- <div
                class="type-header"
                :class="{
                  marg: false
                    // message.generated_title === 'Ask Managr' ||
                    // message.generated_title === 'AI Generated Next Steps',
                }"
              >
                <h4 style="margin-top: 0">
                  {{ userCRM ? `Create Form` : `Connect CRM` }}
                </h4>
              </div> -->

              <!-- v-html="userCRM ? formsMessage : crmMessage" -->
              <div v-if="!userCRM" class="message-text-onboarding">
                <!-- <p class="message-text-p">CRM successfully connected!</p>
                <div class="message-text-button" @click="openConfigChange('forms')">Add Form</div> -->
                <p class="message-text-p">Please connect your CRM to get started.</p>
                <div class="message-text-button" @click="openConfigChange('integrations')">
                  Connect
                </div>
              </div>
              <div
                v-else-if="userCRM && !formsLength && !toggleReady"
                class="message-text-onboarding"
              >
                <!-- <p class="message-text-p">Please connect your CRM.</p>
                <div class="message-text-button" @click="openConfigChange('integrations')">Connect CRM</div> -->
                <p class="message-text-p">Syncing with your CRM. Please wait a few minutes...</p>
                <div style="margin-bottom: 1.5rem" class="center">
                  <div style="width: 23.5vw; margin-top: 1rem" class="progress">
                    <div class="color"></div>
                  </div>

                  <div class="row-between">
                    <!-- <div class="slide-effect">
                      <div :key="statusText" class="slideUp">{{ statusText }}</div>
                    </div> -->

                    <small style="margin: 0; padding: 0">{{ currentTime }}%</small>
                  </div>
                </div>
                <!-- <div class="message-text-button" @click="refreshPage">Refresh</div> -->
              </div>
              <!-- <div v-else-if="!formsLength">
                <p class="message-text-p">Sync complete!</p>
                <div class="message-text-button" @click="refreshPage">Refresh</div>
              </div> -->
              <div v-else class="message-text-onboarding">
                <p class="message-text-p">Sync complete!</p>
                <div class="message-text-button" @click="openConfigChange('forms')">
                  Continue to field mapping
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <!-- <div v-for="(message, i) in conversation.messages" :key="i" class="col-start">
        <div class="message-container">

          <div class="text-container">
            <div style="position: relative">
              <div
                class="type-header"
                v-if="message.user_type === 'bot' && message.generated_title"
                :class="{
                  marg:
                    message.generated_title === 'Ask Managr' ||
                    message.generated_title === 'AI Generated Next Steps',
                }"
              >
                <h4 style="margin-top: 0">
                  {{ message.generated_title }}
                </h4>
                <small v-if="message.resource">
                  {{ message.resource }}
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
                <div class="loading">
                  <div class="dot"></div>
                  <div class="dot"></div>
                  <div class="dot"></div>
                </div>
              </div>

              <div v-else style="margin-top: 1.5rem">
                <div class="column" v-if="message.generated_type === 'email' && addingInstructions">
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
                    regenerate(message.generated_type, message.data, message.id, {
                      data: message.data,
                      integration: message.integration_id,
                      resource: message.resource_type,
                    })
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
                  @click="regenerateEmail(instructionText, message.data, message.id)"
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
          v-if="message.user_type === 'bot' && message.form_id && !message.updated"
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
          v-else-if="message.user_type === 'bot' && message.form_id && message.updated"
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
                <button @click="generateEmail(message.data, message.id)" class="content-button">
                  <font-awesome-icon icon="fa-regular fa-envelope" />Draft follow-up email

                  {{ message.note }}
                </button>
                <button @click="nextSteps(message.data, message.id)" class="content-button">
                  <font-awesome-icon style="height: 10px" icon="fa-solid fa-angles-right" />
                  Suggest next steps
                </button>
                <button
                  @click="
                    getSummary(
                      message.data,
                      message.integration_id,
                      message.resource_type,
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
      </div> -->

      <div style="margin-left: 1rem" v-show="messageLoading" class="loader-container">
        <span
          style="font-size: 20px; margin-right: 0.5rem; padding-top: 0.75rem; margin-left: 0.25rem"
          >🚀</span
        >

        <div style="border-radius: 6px; padding: 0.25rem 0.75rem" class="row">
          <!-- <p>Processing your submission</p> -->
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
      @remove-opp="removeOpp"
      @set-view="setView"
      @get-conversations="getConversations"
      @scroll="scrollToBottom"
      @open-form="emitFormOpen"
      @set-open-form="setOpenForm"
      :messages="messages"
      :conversation="conversation"
    />
  </section>
</template>
  
<script>
import ChatTextBox from './ChatTextBox.vue'
import User from '@/services/users'
import SlackOAuth from '@/services/slack'
import { decryptData } from '../../encryption'

export default {
  name: 'ChatBox',
  components: {
    ChatTextBox,
  },
  props: {
    userCRM: {
      type: String,
    },
    formsLength: {
      type: Boolean,
    },
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
      conversation: null,
      statusText: 'Syncing...',
      currentTime: 0,
      interval: null,
      toggleReady: false,
    }
  },
  watch: {
    messages: 'scrollToBottom',
    currentTime: 'watchTime',
    formsLength: 'watchFormsLength',
  },
  methods: {
    refreshPage() {
      this.$router.go()
    },
    watchFormsLength() {
      if (this.formsLength) {
        this.toggleReady = true
      }
    },
    async getAllForms() {
      const allForms = await SlackOAuth.api.getOrgCustomForm()
      this.$store.commit('SAVE_CRM_FORMS', allForms)
    },
    watchTime() {
      if (this.currentTime >= 100) {
        clearInterval(this.interval)
        this.getAllForms()
        this.toggleReady = true
      }
    },
    startTimer() {
      this.interval = setInterval(() => {
        if (this.currentTime < 100) {
          this.currentTime += 1
        }
      }, 1200)
    },
    openConfigChange(page) {
      this.$emit('open-config-change', page)
    },
    setOpenForm(val) {
      this.$emit('set-open-form', val)
    },
    removeOpp() {
      this.$emit('remove-opp')
    },
    setView(val) {
      this.$emit('set-view', val)
    },
    emitFormOpen(data, open) {
      this.$emit('toggle-chat-modal', data, open)
    },
    async getConversations() {
      try {
        let res = await User.api.getConversations({ user_id: this.user.id })
        this.conversation = res.results[0]
      } catch (e) {
        console.log(e)
      }
    },
    regenerate(type, data, editId, sumObj) {
      this.generatingId = editId
      if (type === 'email') {
        this.addingInstructions = true
      } else if (type === 'next') {
        let newNotes = this.jsonNotes(data, 'meeting_comments')
        this.regenerateNext(newNotes, editId)
      } else {
        this.regenerateSummary(editId, sumObj)
      }
    },
    closeInstructions() {
      this.addingInstructions = false
      this.instructionText = null
    },
    async deleteMessages() {
      if (this.conversation.messages.length) {
        this.messageLoading = true
        try {
          await User.api.deleteMessages().then((response) => {
            this.getConversations()
          })
        } catch (e) {
          console.log()
        } finally {
          this.messageLoading = false
        }
      }
    },
    async regenerateEmail(instructions, note, editId) {
      let newNotes = this.jsonNotes(note, 'meeting_comments')
      this.generating = true
      try {
        await User.api
          .chatEmail({
            id: this.user.id,
            notes: newNotes,
            instructions: instructions,
          })
          .then((response) => {
            if (response.status === 500) {
              User.api
                .editMessage({
                  message_id: editId,
                  error: response.data.value,
                  user_type: 'bot',
                  conversation_id: this.conversation.id,
                  failed: true,
                })
                .then((response) => {
                  this.$refs.chatBox.getConversations()
                })
            } else {
              User.api
                .editMessage({
                  message_id: editId,
                  value: response['res'],
                  user_type: 'bot',
                  conversation_id: this.conversation.id,
                  failed: false,
                  updated: true,
                })
                .then((response) => {
                  this.getConversations()
                })
            }
          })
      } catch (e) {
        console.log(e)
      } finally {
        this.instructionText = null
        this.generating = false
        this.addingInstructions = false
      }
    },
    async regenerateNext(note, editId) {
      this.generating = true
      try {
        let res = await User.api
          .chatNextSteps({
            id: this.user.id,
            notes: note,
          })
          .then((response) => {
            if (response.status === 500) {
              User.api
                .editMessage({
                  error: response.data.value,
                  user_type: 'bot',
                  conversation_id: this.conversation.id,
                  failed: true,
                  message_id: editId,
                })
                .then((response) => {
                  this.$refs.chatBox.getConversations()
                })
            } else {
              User.api
                .editMessage({
                  message_id: editId,
                  value: response['res'],
                  user_type: 'bot',
                  failed: false,
                  updated: true,
                })
                .then((response) => {
                  this.getConversations()
                })
            }
          })
      } catch (e) {
        console.log(e)
      } finally {
        this.generating = false
      }
    },
    async regenerateSummary(editId, sumObj) {
      let jsonData = this.jsonData(sumObj.data)
      this.generating = true
      try {
        let res = await User.api
          .getSummary({
            id: this.user.id,
            data: jsonData,
            integrationId: sumObj.integration,
            resource: sumObj.resource,
          })
          .then((response) => {
            if (response.status === 500) {
              User.api
                .editMessage({
                  message_id: editId,
                  error: response.data.value,
                  user_type: 'bot',
                  conversation_id: this.conversation.id,
                  failed: true,
                })
                .then((response) => {
                  this.$refs.chatBox.getConversations()
                })
            } else {
              User.api
                .editMessage({
                  message_id: editId,
                  value: response['res'],
                  user_type: 'bot',
                  failed: false,
                  updated: true,
                })
                .then((response) => {
                  this.getConversations()
                })
            }
          })
      } catch (e) {
        console.log(e)
      } finally {
        this.generating = false
      }
    },
    async generateEmail(note, id) {
      let newNotes = this.jsonNotes(note, 'meeting_comments')
      this.generating = true
      try {
        let res = await User.api
          .chatEmail({
            id: this.user.id,
            notes: newNotes,
            instructions: null,
          })
          .then((response) => {
            if (response.status === 500) {
              User.api
                .editMessage({
                  message_id: editId,
                  error: response.data.value,
                  user_type: 'bot',
                  conversation_id: this.conversation.id,
                  failed: true,
                })
                .then((response) => {
                  this.$refs.chatBox.getConversations()
                })
            } else {
              User.api
                .editMessage({
                  message_id: id,
                  value: response['res'],
                  user_type: 'bot',
                  failed: false,
                  generated_title: 'AI Generated Email',
                  generated: true,
                  generated_type: 'email',
                })
                .then((response) => {
                  this.getConversations()
                })
            }
          })
      } catch (e) {
        console.log(e)
      } finally {
        this.generating = false
      }
    },
    async nextSteps(note, id) {
      let newNotes = this.jsonNotes(note, 'meeting_comments')
      this.generating = true
      try {
        let res = await User.api
          .chatNextSteps({
            id: this.user.id,
            notes: newNotes,
          })
          .then((response) => {
            if (response.status === 500) {
              User.api
                .editMessage({
                  message_id: editId,
                  error: response.data.value,
                  user_type: 'bot',
                  conversation_id: this.conversation.id,
                  failed: true,
                })
                .then((response) => {
                  this.$refs.chatBox.getConversations()
                })
            } else {
              User.api
                .editMessage({
                  message_id: id,
                  value: response['res'],
                  user_type: 'bot',
                  failed: false,
                  generated_title: 'AI Generated Next Steps',
                  generated: true,
                  generated_type: 'next',
                })
                .then((response) => {
                  this.getConversations()
                })
            }
          })
      } catch (e) {
        console.log(e)
      } finally {
        this.generating = false
      }
    },

    async getSummary(data, integration_id, resource, msg_id) {
      let jsonData = this.jsonData(data)
      this.generating = true
      try {
        let res = await User.api
          .getSummary({
            id: this.user.id,
            data: jsonData,
            integrationId: integration_id,
            resource: resource,
          })
          .then((response) => {
            if (response.status === 500) {
              User.api
                .editMessage({
                  message_id: editId,
                  error: response.data.value,
                  user_type: 'bot',
                  conversation_id: this.conversation.id,
                  failed: true,
                })
                .then((response) => {
                  this.$refs.chatBox.getConversations()
                })
            } else {
              User.api
                .editMessage({
                  message_id: msg_id,
                  value: response['res'],
                  user_type: 'bot',
                  failed: false,
                  generated_title: 'AI Generated Summary',
                  generated: true,
                  generated_type: 'summary',
                })
                .then((response) => {
                  this.getConversations()
                })
            }
          })
      } catch (e) {
        console.log(e)
      } finally {
        this.generating = false
      }
    },
    jsonNotes(data, name) {
      let jsonString = data
      jsonString = jsonString.replace(/'/g, '"')
      jsonString = jsonString.replace(/\bNone\b/g, 'null')
      const obj = JSON.parse(jsonString)
      return obj[name]
    },
    jsonData(data, name) {
      let jsonString = data
      jsonString = jsonString.replace(/'/g, '"')
      jsonString = jsonString.replace(/\bNone\b/g, 'null')
      const obj = JSON.parse(jsonString)
      return obj
    },
    toggleSelectContentOption(i) {
      if (i) {
        this.selectedIndex = i
      }
      this.selectingContent = !this.selectingContent
      // this.scrollToBottom()
    },
    scrollToBottom() {
      setTimeout(() => {
        const chatWindow = this.$refs.chatWindow
        chatWindow.scrollTop = chatWindow.scrollHeight
      }, 200)
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
      // const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
      return this.$store.state.user
    },
    userName() {
      // const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
      return this.$store.state.user.firstName
    },
    chatTitle() {
      return this.$store.state.chatTitle
    },
    messages() {
      return this.$store.state.messages
    },
    currentOpp() {
      return this.$store.state.currentOpp
    },
  },
  created() {
    // this.getConversations()
    // this.scrollToBottom()
    if (this.userCRM && !this.formsLength) {
      this.startTimer()
    }
    if (this.userCRM && this.formsLength) {
      this.toggleReady = true
    }
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
    display: inline-block;
    color: $light-gray-blue;
    margin-bottom: 8px;
  }
}

.message-text {
  font-family: $base-font-family;
  word-wrap: break-word;
  white-space: pre-wrap;
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
    padding-top: 0;
    padding-bottom: 0;
    margin-top: 0;
    margin-bottom: 0;
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
  padding: 1.5rem 0.75rem;
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
.underline {
  text-decoration: underline;
}

.message-text-onboarding {
  // display: flex;
}
.message-text-p {
  // margin-right: 0.5rem;
}

.message-text-button {
  @include primary-button();
  margin-top: 0.5rem;
  width: 11.5rem;
}

.center {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin: 0;
  padding: 0;
}
.progress {
  position: relative;
  height: 24px;
  width: 100%;
  border: 2px solid $soft-gray;
  border-radius: 15px;
}
.progress .color {
  position: absolute;
  background-color: $dark-green;
  width: 0px;
  height: 18px;
  top: 1px;
  border-radius: 15px;
  animation: progres 120s linear;
}
@keyframes progres {
  0% {
    width: 0%;
  }
  25% {
    width: 25%;
  }
  50% {
    width: 50%;
  }
  75% {
    width: 75%;
  }
  100% {
    width: 100%;
  }
}
.text,
.slideDown,
.slideUp {
  position: relative;
  font-size: 13px;
  margin-left: -4px;
  opacity: 0;
}
.slideUp {
  top: 40px;
  left: 10px;
  animation: slideUp ease 0.35s forwards 0.7s;
}

@keyframes slideUp {
  0% {
    transform: translateY(0);
  }
  100% {
    transform: translateY(-40px);
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