<template>
  <div class="container">
    <button class="button" v-if="!showNewEmailBox" @click="showNewEmailBox = !showNewEmailBox">
      Add New Template
    </button>
    <button class="button" v-if="showNewEmailBox" @click="showNewEmailBox = !showNewEmailBox">
      Hide
    </button>
    <div class="box" v-if="showNewEmailBox">
      <div class="box__header">
        <div class="box__title">New Email Template</div>
      </div>
      <div class="box__content">
        <div class="form-element">
          <div class="form-title">Template Name:</div>
          <input type="text" class="input" v-model="newEmailTemplate.name" />
        </div>
        <div class="form-element">
          <div class="form-title">Subject:</div>
          <input type="text" class="input" v-model="newEmailTemplate.subject" />
        </div>
        <div class="form-element">
          <div class="form-title">Email Body:</div>
          <textarea type="text" class="textarea" v-model="newEmailTemplate.bodyHtml" />
        </div>

        <button class="button" @click="addEmailTemplate">Add</button>
      </div>
    </div>
    <div class="box">
      <div class="box__header">
        <div class="box__title">Email Templates</div>
      </div>
      <div class="box__bordered-content" v-if="emailTemplates.length === 0">
        <em>You have no email templates.</em>
      </div>
      <div class="box__bordered-content" v-for="template in emailTemplates" :key="template.id">
        <div class="template-name">Template Name: {{ template.name }}</div>
        <div class="template-subject">Subject: {{ template.subject }}</div>
        <div class="template-body">{{ template.bodyHtml }}</div>
        <button class="button" @click="deleteEmailTemplate(template)">Delete</button>
      </div>
    </div>
  </div>
</template>

<script>
import EmailTemplate from '@/services/email-templates'

export default {
  name: 'EmailTemplates',
  components: {},
  data() {
    return {
      showNewEmailBox: false,
      emailTemplates: [],
      newEmailTemplate: new EmailTemplate(),
    }
  },
  created() {
    this.getEmailTemplates()
  },
  methods: {
    addEmailTemplate() {
      EmailTemplate.api
        .create(this.newEmailTemplate)
        .then(() => {
          this.showNewEmailBox = false
          this.newEmailTemplate = new EmailTemplate()
        })
        .then(() => {
          this.$Alert.alert({
            type: 'success',
            timeout: 4000,
            message: 'Template Added',
          })
        })
        .then(() => {
          this.getEmailTemplates()
        })
    },
    getEmailTemplates() {
      EmailTemplate.api.list().then(data => {
        this.emailTemplates = data.results
      })
    },
    deleteEmailTemplate(emailTemplate) {
      EmailTemplate.api.delete(emailTemplate).then(() => {
        this.getEmailTemplates()
      })
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/layout';
@import '@/styles/containers';
@import '@/styles/mixins/inputs';
@import '@/styles/forms';
.template-name {
  font-weight: 1000;
  margin-bottom: 1.5rem;
}

.template-subject {
  font-weight: 800;
  margin-bottom: 0.5rem;
}
.template-body {
}
</style>
