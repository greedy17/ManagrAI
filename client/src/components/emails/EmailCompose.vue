<template>
  <div>
    <div class="box__tab-header" v-if="replyMessage">
      <div
        class="box__tab"
        @click="toggleActiveTab('reply')"
        :class="{ 'box__tab--active': replyActive }"
      >
        Reply
      </div>
      <div
        class="box__tab"
        @click="toggleActiveTab('replyAll')"
        :class="{ 'box__tab--active': replyAllActive }"
      >
        Reply All
      </div>
    </div>
    <div class="email__row">
      From:
      <div class="email__contact-tag">neil@thinknimble.com</div>
    </div>
    <div class="email__row" v-if="replyMessageId.length > 0">
      Replying to message {{ replyMessageId }}
    </div>
    <div class="email__row">
      To:
      <div class="email__contact-tag" v-for="contactObject in toEmails" :key="contactObject.email">
        {{ contactObject.email }} <span @click="removeEmail(contactObject)">&nbsp;[X]</span>
      </div>

      <span v-if="!showAddBox" @click="showAddBox = !showAddBox">
        [ + ]
      </span>
      <span v-if="showAddBox" @click="showAddBox = !showAddBox">
        [ - ]
      </span>
    </div>
    <div class="box" v-if="showAddBox" style="margin-bottom: .5rem; padding: 2.5rem">
      <div class="flex-container">
        <div class="email__row-title" style="margin-right: 2rem">
          <span>Email:</span>
          <input style="margin-top: .5rem" type="text" class="input" v-model="newContactEmail" />
        </div>
        <div class="email__row-title" style="margin-right: 2rem">
          <span>Name:</span>
          <input style="margin-top: .5rem" type="text" class="input" v-model="newContactName" />
        </div>
      </div>
      <button
        class="button"
        @click="addEmail(generateContactObject(newContactName, newContactEmail))"
      >
        Add New Email
      </button>
    </div>
    <div>
      <div class="email__row-title" v-if="showSubject">
        Subject:
      </div>
      <div class="form-element" v-if="showSubject">
        <input type="text" class="input" />
      </div>
    </div>
    <div>
      <div class="form-element">
        <textarea class="textarea" rows="8" v-model="body"></textarea>
      </div>
    </div>

    <button class="button" @click="sendEmail">Send Email</button>
  </div>
</template>

<script>
import Nylas from '@/services/nylas'
import { mapState } from 'vuex'

export default {
  name: 'EmailCompose',
  components: {},
  props: {
    showSubject: {
      type: Boolean,
      default: true,
    },
    replyMessage: {
      type: Object,
      required: false,
    },
    replyAll: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      replyActive: true,
      replyAllActive: false,
      showAddBox: false,
      newContactEmail: '',
      newContactName: '',
      subject: '',
      body: '',
      toEmails: [],
      ccEmails: [],
      bccEmails: [],
      replyMessageId: '',
    }
  },
  computed: {
    ...mapState(['user']),
  },
  created() {
    if (this.replyMessage && this.replyMessage.from) {
      this.updateToReply()
    }
  },
  methods: {
    toggleActiveTab(tabToActivate) {
      if (tabToActivate === 'reply') {
        this.replyActive = true
        this.replyAllActive = false
        this.updateToReply()
      }
      if (tabToActivate === 'replyAll') {
        this.replyActive = false
        this.replyAllActive = true
        this.updateToReplyAll()
      }
    },
    updateToReply() {
      this.toEmails = this.replyMessage.from
    },
    updateToReplyAll() {
      // We want the email to be "to" whoever sent it.
      let replyEmailTos = this.replyMessage.from
      //   Add in the remaining "to"" emails (not including you) from the original message.
      let otherToEmails = this.replyMessage.to.filter(
        contactObject => contactObject['email'] !== this.user.email,
      )
      const combinedEmailList = replyEmailTos.concat(otherToEmails)
      this.toEmails = combinedEmailList
    },
    generateContactObject(name, email) {
      return {
        name: name,
        email: email,
      }
    },
    addEmail(contactObject) {
      this.toEmails.push(contactObject)
      this.newContactEmail = ''
      this.newContactName = ''
      this.showAddBox = false
    },
    removeEmail(contactObject) {
      this.toEmails = this.toEmails.filter(
        existingContact => existingContact.email !== contactObject.email,
      )
    },
    sendEmail() {
      Nylas.sendEmail(
        this.toEmails,
        this.subject,
        this.body,
        this.ccEmails,
        this.bccEmails,
        this.replyMessageId,
      )
        .then(() => {
          this.$Alert.alert({
            type: 'success',
            timeout: 4000,
            message: 'Email Sent',
          })
        })
        .then(() => {
          this.$emit('emailSent')
        })
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/layout';
@import '@/styles/containers';
@import '@/styles/forms';
@import '@/styles/mixins/inputs';
.filter-green {
  filter: invert(45%) sepia(96%) saturate(2978%) hue-rotate(123deg) brightness(92%) contrast(80%);
}
</style>
