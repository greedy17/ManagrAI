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
      <div class="form__element-header">From:</div>
      <div class="email__contact-tag">neil@thinknimble.com</div>
    </div>
    <EmailList
      :emails="toEmails"
      label="To"
      @add="addToEmail($event)"
      @remove="removeToEmail($event)"
    />
    <EmailList
      :emails="ccEmails"
      label="CC"
      @add="addCCEmail($event)"
      @remove="removeCCEmail($event)"
    />
    <EmailList
      :emails="bccEmails"
      label="BCC"
      @add="addBCCEmail($event)"
      @remove="removeBCCEmail($event)"
    />
    <div class="form__element" v-if="showSubject">
      <div class="form__element-header">Subject</div>
      <input type="text" class="form__input" v-model="subject" />
    </div>
    <div class="form__element">
      <div class="form__element-header">Body</div>
      <textarea class="form__textarea" rows="8" v-model="body"></textarea>
    </div>
    <div class="form__element" v-if="emailTemplates.length > 0">
      <div class="form__element-header">Templates</div>
      <select class="form__select" v-model="activeTemplate" @change="updateBodyWithTemplate">
        <option :value="template" v-for="template in emailTemplates" :key="template.id">{{
          template.name
        }}</option>
      </select>
    </div>
    <div class="flexbox-container" style="margin-top: 1rem; justify-content: space-between">
      <button class="button" @click="previewEmail">Preview Email</button>
      <button class="button" @click="sendEmail">Send Email</button>
    </div>
    <div class="box" v-if="previewActive">
      <div class="box__header">
        <div class="box__content">
          <strong>{{ preview.subject }}</strong>
        </div>
      </div>
      <div class="box__content">
        {{ preview.body }}
      </div>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex'

import EmailList from '@/components/emails/EmailList'

import Nylas from '@/services/nylas'
import EmailTemplate from '@/services/email-templates'

export default {
  name: 'EmailCompose',
  components: { EmailList },
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
      activeTemplate: {},
      emailTemplates: [],
      preview: {},
      previewActive: false,
      replyActive: true,
      replyAllActive: false,
      subject: '',
      body: '',
      toEmails: [],
      ccEmails: [],
      bccEmails: [],
      replyMessageId: '',
      // NOTE: WHEN WE EVENTUALY MOVE THIS OVER TO ANOTHER COMPONENT, WE WILL HAVE TO FIGURE OUT
      // HOW TO PASS IN THE VARIABLES. I'M GOING TO HOLD ON THIS UNTIL WE FIGURE OUT HOW TO INTEGRATE
      // IT WITH THE LEAD PAGE.
      variables: {
        first_name: 'Neil',
        last_name: 'Shah',
        company: 'The Banana Republic',
      },
    }
  },
  computed: {
    ...mapState(['user']),
  },
  created() {
    if (this.replyMessage && this.replyMessage.from) {
      this.replyMessageId = this.replyMessage.id
      this.updateToReply()
    }
    this.getEmailTemplates()
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
      this.ccEmails = this.replyMessage.cc.filter(
        contactObject => contactObject['email'] !== this.user.email,
      )
      this.bccEmails = this.replyMessage.bcc.filter(
        contactObject => contactObject['email'] !== this.user.email,
      )
    },
    updateToReplyAll() {
      // We want the email to be "to" whoever sent it.
      let replyEmailTos = this.replyMessage.from
      // Add in the remaining "to"" emails (not including you) from the original message.
      let otherToEmails = this.replyMessage.to.filter(
        contactObject => contactObject['email'] !== this.user.email,
      )
      const combinedEmailList = replyEmailTos.concat(otherToEmails)
      this.toEmails = combinedEmailList
      this.ccEmails = this.replyMessage.cc.filter(
        contactObject => contactObject['email'] !== this.user.email,
      )
      this.bccEmails = this.replyMessage.bcc.filter(
        contactObject => contactObject['email'] !== this.user.email,
      )
    },
    addToEmail(contactObject) {
      this.toEmails.push(contactObject)
    },
    addCCEmail(contactObject) {
      this.ccEmails.push(contactObject)
    },
    addBCCEmail(contactObject) {
      this.bccEmails.push(contactObject)
    },
    removeToEmail(contactObject) {
      this.toEmails = this.toEmails.filter(
        existingContact => existingContact.email !== contactObject.email,
      )
    },
    removeCCEmail(contactObject) {
      this.ccEmails = this.ccEmails.filter(
        existingContact => existingContact.email !== contactObject.email,
      )
    },
    removeBCCEmail(contactObject) {
      this.bccEmails = this.bccEmails.filter(
        existingContact => existingContact.email !== contactObject.email,
      )
    },
    updateBodyWithTemplate() {
      this.subject = this.activeTemplate.subject
      this.body = this.activeTemplate.bodyHtml
    },
    getEmailTemplates() {
      EmailTemplate.api.list().then(data => {
        this.emailTemplates = data.results
      })
    },
    sendEmail() {
      Nylas.sendEmail(
        this.toEmails,
        this.subject,
        this.body,
        this.ccEmails,
        this.bccEmails,
        this.replyMessageId,
        this.variables,
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
    previewEmail() {
      this.previewActive = true
      Nylas.previewEmail(
        this.toEmails,
        this.subject,
        this.body,
        this.ccEmails,
        this.bccEmails,
        this.replyMessageId,
        this.variables,
      ).then(response => {
        this.preview = response.data
      })
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/layout';
@import '@/styles/containers';
@import '@/styles/forms';
@import '@/styles/emails';
@import '@/styles/mixins/inputs';
.filter-green {
  filter: invert(45%) sepia(96%) saturate(2978%) hue-rotate(123deg) brightness(92%) contrast(80%);
}

.new-email-box {
  width: 100%;
  display: flex;
  justify-content: space-evenly;
  align-items: center;
}

.add-new-contact-button {
  @include primary-button;
  padding: 0.5rem;
}
</style>
