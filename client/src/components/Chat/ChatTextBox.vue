<template>
  <section class="input-section">
    <Transition name="slide-fade">
      <div v-if="templatesOpen" class="templates">
        <section class="section">
          <header style="border-top: none" class="template-header">
            <span class="gray-bg"> 🦾 </span>
            <p class="gray-title">Actions</p>
            <small @click="toggleTemplates" class="automarginleft">x</small>
          </header>
          <div class="template-body">
            <p @click="addTemplate(action.value)" v-for="(action, i) in actions" :key="i">
              {{ action.name }}
            </p>
          </div>
        </section>

        <!-- <section class="section">
          <header class="template-header">
            <span class="blue-bg">
              <img src="@/assets/images/article.svg" class="blue-filter" height="14px" alt="" />
            </span>
            <p class="gray-title">Note templates</p>
          </header>
          <div class="template-body">
            <p>1st template</p>
            <p>2nd template</p>
          </div>
        </section> -->
      </div>
    </Transition>

    <div class="input-container">
      <div class="main-text">
        <span
          :class="{ activeicon: templatesOpen }"
          @click="toggleTemplates"
          style="cursor: pointer; font-size: 14px; margin-bottom: 2px"
        >
          ⚡️
        </span>
        <textarea
          @keydown.enter.exact.prevent="sendMessage"
          class="area-input"
          rows="1"
          placeholder="What would you like to do?"
          v-model="message"
          v-autoresize
          ref="chatTextArea"
        />
        <font-awesome-icon
          :class="{ invert: !message }"
          class="gray"
          style="margin-bottom: 4px; height: 14px; cursor: pointer"
          icon="fa-regular fa-paper-plane"
          @click="sendMessage"
        />
      </div>
    </div>
  </section>
</template>

<script>
// import Conversation from '@/services/conversations/models'
import User from '@/services/users'

export default {
  name: 'ChatTextBox',
  components: {},
  props: {
    messages: {
      type: Array,
    },
    scrollToBottom: {
      type: Function,
    },
  },
  data() {
    return {
      message: '',
      templatesOpen: false,
      chatRes: null,
      actions: [
        { name: 'Update Record', value: 'Update Opportunity' },
        { name: 'Create Record', value: 'Create Opportunity' },
        { name: 'Ask Managr', value: 'Ask managr' },
        { name: 'Run Review', value: 'Run Review for Opportunity' },
        { name: 'Deal Updates', value: 'Get Summary for Opportunity' },
        { name: 'Call Summary', value: 'Get call summary for Opportunity' },
        { name: 'Call Analysis', value: 'Get call analysis for Opportunity' },
      ],
    }
  },

  methods: {
    testBox() {
      this.message = ''
      setTimeout(() => {
        this.$refs.chatTextArea.dispatchEvent(new Event('textarea-clear'))
      }, 100)
    },
    async sendMessage() {
      if (this.message.length > 3) {
        let chatmsg = this.message
        this.$emit('set-message', { user: 'user', value: chatmsg })
        this.$emit('message-loading', true)
        this.message = ''
        try {
          setTimeout(() => {
            this.$refs.chatTextArea.dispatchEvent(new Event('textarea-clear'))
          }, 100)
          let res = await User.api.chatUpdate({
            user_id: this.user.id,
            prompt: chatmsg,
            resource_type: this.user.crm === 'HUBSPOT' ? 'Deal' : 'Opportunity',
          })
          this.chatRes = res
          this.$emit('set-message', {
            user: 'bot',
            id: this.chatRes['id'],
            value: this.chatRes['res'][0],
            resource: this.chatRes['resource'][0],
            formId: this.chatRes['form'],
            data: this.chatRes['data'],
            resourceId: this.chatRes['resourceId'],
            formType: this.chatRes['formType'],
            integrationId: this.chatRes['integrationId'],
            resourceType: this.chatRes['resourceType'],
            updated: false,
          })
          this.$emit('set-title', this.chatRes['resource'][0] || 'Uh-oh')
        } catch (e) {
          console.log(e)
        } finally {
          this.$emit('message-loading', false)
          this.scrollToBottom()
        }
      }
    },
    addNewLine() {
      console.log('here')
      this.message += '\n'
    },
    addTemplate(val) {
      this.message = val
      this.toggleTemplates()
    },

    toggleTemplates() {
      this.templatesOpen = !this.templatesOpen
    },
  },
  computed: {
    user() {
      return this.$store.state.user
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

.input-section {
  display: flex;
  align-items: center;
  padding: 1rem 1rem 0 1rem;
  width: 100%;
  background-color: white;
  margin-bottom: -0.25rem;
  position: relative;
}

.main-text {
  display: flex;
  align-items: flex-end;
  padding: 0;
  margin: 0;
}

.input-container {
  flex-wrap: nowrap;
  border: 1px solid rgba(0, 0, 0, 0.1);
  padding: 0.75rem 1rem;
  border-radius: 6px;
  width: 100%;
  background-color: white;
  color: $base-gray;
}

.area-input {
  width: 96%;
  max-height: 250px;
  padding: 0 1rem;
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

.templates {
  // border: 1px solid rgba(0, 0, 0, 0.1);
  min-height: 60px;
  width: 250px;
  position: absolute;
  padding-bottom: 0.5rem;
  bottom: 3.5rem;
  border-radius: 6px;
  background-color: white;
  box-shadow: 0 0 11px #b8bdc2;
}

.template-header {
  display: flex;
  align-items: center;
  // background-color: $soft-gray;
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
</style>