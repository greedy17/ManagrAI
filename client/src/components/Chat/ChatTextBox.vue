<template>
  <section class="input-section">
    <div class="input-container">
      <div class="input-row">
        <div class="main-text">
          <p class="current" v-if="currentOpp && currentOpp !== true">
            {{ currentOpp.name }}
            <span class="remove" @click="clearMessage">x</span>
          </p>
          <button v-if="!textBoxType" @click="openActions" class="action-button">
            <img src="@/assets/images/sparkle.svg" height="14px" alt="" />Select Action
          </button>

          <div v-else class="current-action">
            <img :src="require(`@/assets/images/${currentAction.img}.svg`)" height="12px" alt="" />
            {{ currentAction.name }}
            <span @click="clearAction" class="remove-action">x</span>
          </div>
          <Transition name="slide-fade">
            <div v-if="showMessage" class="templates">
              <p>
                Select a record from the list
                <img class="inverted" src="@/assets/images/arrow-right.svg" height="10px" alt="" />
              </p>
            </div>
          </Transition>
          <Transition name="slide-fade">
            <div v-if="showMeetingMessage" class="templates">
              <p>
                Select a meeting from the list
                <img class="inverted" src="@/assets/images/arrow-right.svg" height="10px" alt="" />
              </p>
            </div>
          </Transition>

          <div class="action-templates" v-if="templatesOpen">
            <div class="header">
              <h5 class="action-title">
                <img src="@/assets/images/sparkle.svg" height="12px" alt="" />Actions
              </h5>

              <div @click="toggleTemplates">
                <p>X</p>
              </div>
            </div>
            <!-- :class="{ 'current-actions': currentOpp && textBoxType === action.value }" -->
            <p
              class="action-item"
              @click="addTemplate(action)"
              v-for="(action, i) in actions"
              :key="i"
            >
              <img :src="require(`@/assets/images/${action.img}.svg`)" height="12px" alt="" />
              {{ action.name }}
            </p>
          </div>
        </div>
        <textarea
          @keydown.enter.exact.prevent="sendMessage"
          class="area-input"
          rows="1"
          :placeholder="placeholder"
          v-model="message"
          :disabled="!actionSelected || !currentOpp"
          v-autoresize
          autofocus
          ref="chatTextArea"
        />

        <img
          :class="{ invert: !message }"
          src="@/assets/images/paper-plane.svg"
          height="14px"
          alt=""
        />
      </div>
    </div>
  </section>
</template>

<script>
// import Conversation from '@/services/conversations/models'
import User from '@/services/users'
import { decryptData } from '../../encryption'

export default {
  name: 'ChatTextBox',
  components: {},
  props: {
    messages: {
      type: Array,
    },
    conversation: {},
  },
  data() {
    return {
      message: '',
      showMessage: false,
      templatesOpen: false,
      showMeetingMessage: false,
      chatRes: null,
      chatmsg: null,
      actionSelected: false,
      textBoxType: '',
      placeholder: '',
      currentAction: null,
      actions: [
        { name: 'Log Meeting', value: 'Log Meeting', img: 'calendar' },
        { name: 'Update', value: 'Open Form', img: 'edit-note' },
        {
          name: 'Add Notes',
          value: 'Update',
          img: 'notebook',
        },
        { name: 'Ask Managr', value: 'Ask Managr', img: 'comment' },
        { name: 'Inspect Deal', value: 'Run Review', img: 'money' },
        // { name: 'Call Summary', value: 'Get call summary for Opportunity' },
        // { name: 'Call Analysis', value: 'Get call analysis for Opportunity' },
      ],
    }
  },
  mounted() {
    this.setPlaceholder()
  },
  watch: {
    currentOpp: 'setPlaceholder',
  },
  methods: {
    scrollToBottom() {
      this.$emit('scroll')
    },
    clearAction() {
      this.actionSelected = false
      this.textBoxType = null
      this.setPlaceholder()
      this.message = ''
      this.currentAction = null
    },
    openActions() {
      if (!this.currentOpp) {
        this.toggleMessage()
        this.$emit('set-view', 'pipeline')
      } else {
        this.toggleTemplates()
      }
    },
    setPlaceholder() {
      // console.log('bools', this.userCRM, !this.displayedOpps.results.length)
      // console.log('bools', this.$store.state.chatOpps)
      // if (this.userCRM && !(this.displayedOpps.results && this.displayedOpps.results.length)) {
      //   this.templatesOpen = false
      //   this.actionSelected = false
      //   this.textBoxType = null
      //   this.message = ''
      //   this.currentAction = null
      //   this.placeholder = 'Sync in progress...'
      // }
      // else 
      if (!this.currentOpp) {
        this.templatesOpen = false
        this.actionSelected = false
        this.textBoxType = null
        this.message = ''
        this.currentAction = null
        this.placeholder = 'Select a record...'
      } else if (this.currentOpp && !this.actionSelected) {
        this.placeholder = 'Select an action...'
      }
    },
    testBox() {
      this.message = ''
      setTimeout(() => {
        this.$refs.chatTextArea.dispatchEvent(new Event('textarea-clear'))
      }, 100)
    },
    clearMessage() {
      this.actionSelected = false
      this.textBoxType = null
      this.placeholder = null
      this.message = ''
      this.$emit('remove-opp')
    },
    async sendMessage() {
      if (this.currentOpp && this.message) {
        this.chatmsg = this.message
        try {
          await User.api
            .addMessage({
              value: this.message,
              user_type: 'user',
              conversation_id: this.conversation.id,
              data: {},
            })
            .then((response) => {
              this.$emit('get-conversations')
              this.message = ''
              this.$emit('message-loading', true)
              setTimeout(() => {
                this.$refs.chatTextArea.dispatchEvent(new Event('textarea-clear'))
              }, 100)
              this.scrollToBottom()
            })
          if (this.textBoxType === 'Ask Managr') {
            this.askManagr()
          } else if (this.textBoxType === 'Update') {
            this.chatUpdate()
          }
        } catch (e) {
          console.log(e)
        }
      }
    },
    async askManagr() {
      try {
        let res = await User.api
          .askManagr({
            user_id: this.user.id,
            prompt: `Ask Managr ${this.chatmsg}`,
            resource_type: this.user.crm === 'HUBSPOT' ? 'Deal' : 'Opportunity',
            resource_id: this.$store.state.currentOpp.id,
          })
          .then((response) => {
            if (response.status >= 400 && response.status < 500) {
              User.api
                .addMessage({
                  error: response.data.value,
                  user_type: 'bot',
                  conversation_id: this.conversation.id,
                  failed: true,
                  data: {},
                })
                .then((response) => {
                  this.$emit('get-conversations')
                })
            } else if (response.status === 500) {
              User.api
                .addMessage({
                  error: 'Timeout error, try again',
                  user_type: 'bot',
                  conversation_id: this.conversation.id,
                  failed: true,
                  data: {},
                })
                .then((response) => {
                  this.$emit('get-conversations')
                })
            } else {
              User.api
                .addMessage({
                  value: response['res'],
                  user_type: 'bot',
                  conversation_id: this.conversation.id,
                  failed: false,
                  data: {},
                  resource_id: response['resourceId'],
                  resource_type: response['resourceType'],
                  updated: false,
                  generated_title: 'Ask Managr',
                })
                .then((response) => {
                  this.$emit('get-conversations')
                })
            }
          })
      } catch (e) {
        console.log(e)
        this.$emit('message-loading', false)
      } finally {
        this.$emit('message-loading', false)
        this.scrollToBottom()
      }
    },
    async dealReview(msg) {
      this.$emit('message-loading', true)
      try {
        let res = await User.api
          .dealReview({
            user_id: this.user.id,
            prompt: msg,
            resource_type: this.user.crm === 'HUBSPOT' ? 'Deal' : 'Opportunity',
            resource_id: this.currentOpp.id,
          })
          .then((response) => {
            if (response.status >= 400 && response.status < 500) {
              User.api
                .addMessage({
                  error: response.data.value,
                  user_type: 'bot',
                  conversation_id: this.conversation.id,
                  failed: true,
                  data: {},
                })
                .then((response) => {
                  this.$emit('get-conversations')
                })
            } else if (response.status === 500) {
              User.api
                .addMessage({
                  error: 'Timeout error, try again',
                  user_type: 'bot',
                  conversation_id: this.conversation.id,
                  failed: true,
                  data: {},
                })
                .then((response) => {
                  this.$emit('get-conversations')
                })
            } else {
              User.api
                .addMessage({
                  value: response['res'],
                  user_type: 'bot',
                  conversation_id: this.conversation.id,
                  failed: false,
                  data: {},
                  resource_id: response['resourceId'],
                  resource_type: response['resourceType'],
                  updated: false,
                  generated_title: 'Deal Review',
                })
                .then((response) => {
                  this.$emit('get-conversations')
                })
            }
          })
      } catch (e) {
        console.log(e)
        this.$emit('message-loading', false)
      } finally {
        this.clearMessage()
        this.$emit('message-loading', false)
        this.scrollToBottom()
      }
    },
    async chatUpdate() {
      try {
        let res = await User.api
          .chatUpdate({
            user_id: this.user.id,
            prompt: `Update ${this.currentOpp.name} ${this.chatmsg}`,
            resource_type: this.user.crm === 'HUBSPOT' ? 'Deal' : 'Opportunity',
          })
          .then((response) => {
            this.chatRes = response
            if (response.status >= 400 && response.status < 500) {
              console.log(response)
              User.api
                .addMessage({
                  error: response.data.value,
                  user_type: 'bot',
                  conversation_id: this.conversation.id,
                  failed: true,
                  data: {},
                })
                .then((response) => {
                  this.$emit('get-conversations')
                })
            } else if (response.status === 500) {
              User.api
                .addMessage({
                  error: 'Timeout error, try again',
                  user_type: 'bot',
                  conversation_id: this.conversation.id,
                  failed: true,
                  data: {},
                })
                .then((response) => {
                  this.$emit('get-conversations')
                })
            } else {
              User.api
                .addMessage({
                  user_type: 'bot',
                  conversation_id: this.conversation.id,
                  failed: false,
                  value: response['res'][0],
                  resource: response['resource'][0],
                  form_id: response['form'],
                  data: response['data'],
                  resource_id: response['resourceId'],
                  form_type: response['formType'],
                  integration_id: response['integrationId'],
                  resource_type: response['resourceType'],
                  updated: false,
                })
                .then((response) => {
                  this.$emit('get-conversations')
                })
            }
          })
      } catch (e) {
        console.log(e)
        this.$emit('message-loading', false)
      } finally {
        this.$emit('set-title', this.chatRes['resource'][0] || 'Uh-oh')
        this.$emit('message-loading', false)
        this.scrollToBottom()
      }
    },
    addNewLine() {
      this.message += '\n \n \n \n'
    },

    addTemplate(val) {
      this.currentAction = val
      this.textBoxType = null
      this.placeholder = null
      this.message = ''
      this.templatesOpen = false

      if (val.value.toLowerCase().includes('update')) {
        if (this.currentOpp) {
          this.$emit('set-open-form', false)
          this.actionSelected = true
          this.textBoxType = 'Update'
          this.placeholder = `Add your notes for ${this.currentOpp.name}...`
          this.$nextTick(() => {
            this.$refs.chatTextArea.focus()
          })
        } else {
          this.toggleMessage()
        }
      } else if (val.value.toLowerCase().includes('log meeting')) {
        if (this.currentMeeting) {
        } else {
          this.$emit('set-view', 'meetings')
          this.toggleMeetingMessage()
        }
      } else if (val.value.toLowerCase().includes('ask managr')) {
        if (this.currentOpp) {
          this.actionSelected = true
          this.textBoxType = 'Ask Managr'
          this.placeholder = `Ask Managr anything about ${this.currentOpp.name}...`
          this.$nextTick(() => {
            this.$refs.chatTextArea.focus()
          })
        } else {
          this.toggleMessage()
        }
      } else if (val.value.toLowerCase().includes('run review')) {
        if (this.currentOpp) {
          this.textBoxType = 'Run Review'
          this.placeholder = `Running review for ${this.currentOpp.name}...`
          this.actionSelected = false
          this.dealMessage()
        } else {
          this.toggleMessage()
        }
      } else if (val.value.toLowerCase().includes('open form')) {
        if (this.currentOpp) {
          console.log('MADE IT TO STEP ONE')
          this.$emit('open-form', this.currentOpp.secondary_data, true)
          this.actionSelected = false
          this.textBoxType = 'Open Form'
        }
      } else if (!val.value.toLowerCase().includes('log meeting')) {
        this.$emit('set-view', 'pipeline')
        this.actionSelected = true
      }
    },
    async dealMessage() {
      try {
        await User.api
          .addMessage({
            value: `Run review for ${this.currentOpp.name}`,
            user_type: 'user',
            conversation_id: this.conversation.id,
            data: {},
          })
          .then((response) => {
            this.$emit('get-conversations')
            this.scrollToBottom()
            this.dealReview(`Run review for ${this.currentOpp.name}`)
          })
      } catch (e) {
        console.log(e)
      } finally {
      }
    },
    toggleMessage() {
      this.showMessage = true
      this.showMeetingMessage = false
      setTimeout(() => {
        this.showMessage = false
      }, 1750)
    },
    toggleMeetingMessage() {
      this.showMeetingMessage = true
      this.showMessage = false
      setTimeout(() => {
        this.showMeetingMessage = false
      }, 1750)
    },
    toggleTemplates() {
      this.templatesOpen = !this.templatesOpen
    },
  },
  computed: {
    user() {
      // const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
      return this.$store.state.user
    },
    displayedOpps: {
      get() {
        return this.$store.state.chatOpps
      },

      set(value) {
        this.displayedOpps = value
      },
    },
    userCRM() {
      // const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
      return this.$store.state.user.crm
    },
    currentOpp() {
      return this.$store.state.currentOpp
    },
    currentMeeting() {
      return this.$store.state.currentMeeting
    },
  },
  directives: {
    autoresize: {
      inserted(el) {
        // el.style.overflow = 'scro'

        function adjustTextareaHeight() {
          el.style.height = 'auto'
          el.style.height = el.scrollHeight + 'px'
        }

        el.addEventListener('input', adjustTextareaHeight)
        el.addEventListener('focus', adjustTextareaHeight)
        el.addEventListener('textarea-clear', adjustTextareaHeight)
        adjustTextareaHeight()
      },
    },
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

@keyframes shake {
  0% {
    transform: translateX(0);
  }
  25% {
    transform: translateX(5px);
  }
  50% {
    transform: translateX(-5px);
  }
  75% {
    transform: translateX(5px);
  }
  100% {
    transform: translateX(0);
  }
}

.action-templates {
  // animation: shake 0.3s 1;
  display: block;
  width: 194px;
  position: absolute;
  bottom: 0;
  left: 1rem;
  font-size: 12px;
  background: white;
  padding: 0.25rem 0.5rem;
  border-radius: 5px;
  box-shadow: 0 11px 16px rgba(0, 0, 0, 0.1);
  line-height: 1.5;
  z-index: 2000;
  border: 1px solid rgba(0, 0, 0, 0.1);

  p {
    margin-top: 8px;
    padding: 0;
  }
}

.action-templates::before {
  position: absolute;
  height: 8px;
  width: 8px;
  background: $dark-green;
  transform: translate(-50%) rotate(45deg);
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.input-row {
  display: flex;
  align-items: center;
  flex-direction: row;
  align-items: center;
}

.current-actions {
  border: 1px solid $dark-green !important;
  color: $dark-green !important;
}

.input-section {
  display: flex;
  align-items: center;
  padding: 1rem 1rem 0 1rem;
  width: 100%;
  // background-color: white;
  margin-bottom: -0.25rem;
  position: relative;
}

.dampen {
  filter: invert(40%);
}

.gold-filter {
  filter: invert(89%) sepia(43%) saturate(4130%) hue-rotate(323deg) brightness(96%) contrast(87%);
  margin-bottom: -2px;
}

.remove {
  background-color: rgba(0, 0, 0, 0.4);
  z-index: 4;
  cursor: pointer;
  padding: 6px 4px;
  border-radius: 3px;
  position: absolute;
  right: 0;
  bottom: 0;
}

.main-text {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: flex-start;
  border-right: 1px solid rgba(0, 0, 0, 0.1);
  padding-right: 1.25rem;
  margin: 0;
}

.current {
  width: 137px;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  background-color: $dark-black-blue;
  color: white !important;
  border: 1px solid $dark-black-blue;
  cursor: text !important;
  padding: 6px 1.2rem !important;
  border-radius: 5px;
  position: relative;
}

// .action {
//   display: flex;
//   flex-direction: row;
//   align-items: center;
//   width: 100%;
//   position: relative;
//   &__p {
//     padding: 0.25rem 0.5rem;
//     margin: 0 0.5rem;
//     color: $light-gray-blue;
//     cursor: pointer;
//     border-radius: 4px;
//     font-size: 12px;
//     background-color: white;
//     border: 1px solid rgba(0, 0, 0, 0.1);
//     white-space: nowrap;
//     // max-width: 150px;
//     overflow: hidden;
//     text-overflow: ellipsis;
//   }
// }

.input-container {
  flex-wrap: nowrap;
  border: 1px solid rgba(0, 0, 0, 0.1);
  padding: 0.75rem 1.2rem 0.75rem 1.2rem;
  border-radius: 6px;
  width: 100%;
  background-color: $offer-white;
  color: $base-gray;
}

.area-input {
  width: 100%;
  background-color: $offer-white;
  margin-bottom: 0.25rem;
  max-height: 250px;
  padding: 0 1.25rem;
  line-height: 1.75;
  outline: none;
  border: none;
  letter-spacing: 0.5px;
  font-size: 14px;
  font-family: $base-font-family !important;
  border: none !important;
  resize: none;
  text-align: left;
  overflow: auto;
  scroll-behavior: smooth;
}

.area-input:disabled {
  cursor: not-allowed;
}

.area-input::-webkit-scrollbar {
  width: 6px;
  height: 0px;
}
.area-input::-webkit-scrollbar-thumb {
  background-color: $base-gray;
  box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
  border-radius: 6px;
}

.invert {
  filter: invert(60%);
}
.activemargin {
  padding-left: 1rem;
}
.activeicon {
  animation: shimmer 1s infinite;
  -webkit-mask: linear-gradient(-60deg, #000 30%, #0005, #000 70%) right/200% 100%;
}
.gray {
  color: rgb(82, 80, 80);
}
.gray-title {
  font-size: 14px;
  color: $base-gray;
  letter-spacing: 0.5px;
}

.template-header {
  display: flex;
  align-items: center;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  padding: 0 1rem;

  p {
    margin: 0.75rem 0;
  }

  span {
    margin-right: 1rem;
    display: block;
    border-radius: 100%;
    margin-left: -4px;
  }
}

.template-body {
  display: flex;
  align-items: flex-start;
  flex-direction: column;

  p {
    border-radius: 100%;
    padding-left: 3rem;
    margin: 0.5rem 0.25rem;
    color: $base-gray;
    cursor: pointer;
    width: 100%;

    &:hover {
      color: $light-gray-blue;
    }
  }
}

.template-close {
  width: 100%;

  display: flex;
  align-items: flex-end;
  justify-content: flex-end;
  font-size: 18px;

  color: #8e8e8e;

  span {
    margin-right: -0.25rem;
  }
}

.blue-bg {
  background-color: #cad8fa;
  padding: 2px 4px 0px 4px;
}

.blue-filter {
  filter: invert(61%) sepia(69%) saturate(4249%) hue-rotate(204deg) brightness(100%) contrast(104%);
}

.gray-bg {
  background-color: #c5c4c4;
  font-size: 10px;
  padding: 4px 6px;
  border-radius: 100%;
  margin-left: -4px;
  margin-right: 0.25rem;
}

/*
  Enter and leave animations can use different
  durations and timing functions.
*/
.slide-fade-enter-active {
  transition: all 0.2s ease-in;
}

.slide-fade-leave-active {
  transition: all 0.1s ease-out;
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  transform: translateY(100px);
}

.automarginleft {
  margin-left: auto;
  font-size: 18px;
  color: $light-gray-blue;
  margin-top: -0.25rem;
  cursor: pointer;
}

.tooltip {
  display: block;
  width: 228px;
  height: auto;
  position: absolute;
  top: 0;
  font-size: 14px;
  background: $base-gray;
  color: white;
  padding: 6px 8px;
  border-radius: 5px;
  box-shadow: 0 10px 10px rgba(0, 0, 0, 0.1);
  opacity: 0;
  pointer-events: none;
  line-height: 1.5;
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);

  header {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: space-between;

    p {
      margin: 0;
      padding: 0;
      margin-top: 0.25rem;
    }

    p:last-of-type {
      cursor: pointer;
      margin-top: -4px;
    }
  }
}

.tooltip::before {
  position: absolute;
  content: '';
  height: 8px;
  width: 8px;
  background: $base-gray;
  bottom: -3px;
  left: 50%;
  transform: translate(-50%) rotate(45deg);
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.showing-tooltip {
  top: -30px;
  opacity: 1;
  visibility: visible;
  pointer-events: auto;
  text-shadow: 0px -1px 0px rgba(0, 0, 0, 0.1);
}

.templates-green {
  // animation: shake 0.3s 1;
  display: block;
  width: fit-content;
  height: 40px;
  position: absolute;
  top: -1.75rem;
  left: 40%;
  font-size: 12px;
  background: $dark-black-blue;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 5px;
  box-shadow: 0 10px 10px rgba(0, 0, 0, 0.1);
  pointer-events: none;
  line-height: 1.5;
  z-index: 20;

  p {
    margin-top: 8px;
    padding: 0;
  }
}

.templates-green::before {
  position: absolute;
  // content: '';
  height: 8px;
  width: 8px;
  background: $dark-green;
  // bottom: -3px;
  // left: 10%;
  transform: translate(-50%) rotate(45deg);
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.templates {
  // animation: shake 0.3s 1;
  display: block;
  width: fit-content;
  height: 40px;
  position: absolute;
  top: -1.25rem;
  left: 2.1rem;
  font-size: 12px;
  background: $coral;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 5px;
  box-shadow: 0 10px 10px rgba(0, 0, 0, 0.1);
  pointer-events: none;
  line-height: 1.5;
  z-index: 20;

  p {
    margin-top: 8px;
    padding: 0;
  }
}

.templates::before {
  position: absolute;
  content: '';
  height: 8px;
  width: 8px;
  background: $coral;
  bottom: -3px;
  left: 10%;
  transform: translate(-50%) rotate(45deg);
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.current-action {
  @include chat-button();
  color: $dark-black-blue;
  padding-top: 7px;
  padding-bottom: 7px;
  width: 137px;
  position: relative;
  cursor: text;
  img {
    margin-right: 0.5rem;
    filter: invert(25%) sepia(10%) saturate(1618%) hue-rotate(162deg) brightness(91%) contrast(91%);
  }

  &:hover {
    scale: 1;
    box-shadow: none;
  }
}

.remove-action {
  background-color: rgba(0, 0, 0, 0.1);
  color: $dark-black-blue;
  z-index: 4;
  cursor: pointer;
  height: 99.5%;
  padding: 6px 4px;
  border-radius: 3px;
  position: absolute;
  right: 0;
  bottom: 0;
}

.action-button {
  @include chat-button();
  color: $dark-black-blue;
  padding-top: 10px;
  padding-bottom: 10px;
  overflow: hidden;
  text-overflow: ellipsis;
  img {
    margin-right: 0.5rem;
    filter: invert(25%) sepia(10%) saturate(1618%) hue-rotate(162deg) brightness(91%) contrast(91%);
  }
}

.header {
  display: flex;
  align-items: center;
  flex-direction: row;
  justify-content: space-between;
  padding: 0 0.25rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  width: 100%;

  p {
    color: $light-gray-blue;
    font-size: 11px;
    padding: 2px 2px 0px 2px;
    cursor: pointer;
  }
}

.action-title {
  display: flex;
  align-items: center;
  font-size: 13px;
  margin: 0;
  padding: 0;
  img {
    margin-right: 0.75rem;
  }
}

.action-item {
  display: flex;
  align-items: center;
  flex-direction: row;
  font-size: 13px;
  padding: 2px 0 !important;
  padding-left: 1rem;
  cursor: pointer;
  position: relative;
  width: 100%;
  img {
    margin: 0 0.75rem 0 0.25rem;
  }

  p {
    white-space: nowrap;
    text-overflow: ellipsis;
    overflow: hidden;
    width: 100%;
    margin: 0;
  }

  &:hover {
    opacity: 0.65;
  }
}

.action-item:first-of-type {
  margin-top: 12px !important;
}

.inverted {
  filter: invert(99%);
  margin-left: 4px;
}
</style>