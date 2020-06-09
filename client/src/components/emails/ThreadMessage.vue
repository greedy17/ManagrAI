<template>
  <div class="actions__item">
    <div class="actions__row">
      <div class="actions__item-header-icon">
        <img
          alt="icon"
          :src="require(`@/assets/images/email.svg`)"
          @click="isExpanded = !isExpanded"
          :class="{ 'filter-green': isExpanded }"
          class="icon"
        />
      </div>

      <div class="actions__item-header-title">
        {{ message.subject }}<br /><em v-if="!isExpanded">{{ message.snippet }}</em>
      </div>
      <div class="actions__item-header-date" v-if="!isExpanded">
        From:<br />
        <div v-for="(contact, index) in message.from" class="email__contact-tag" :key="index">
          {{ contact.email }}
        </div>
      </div>
      <div class="actions__item-header-date" v-if="!isExpanded">
        To:<br />
        <div v-for="(contact, index) in message.to" class="email__contact-tag" :key="index">
          {{ contact.email }}
        </div>
      </div>
    </div>
    <div class="email__row" v-if="isExpanded">
      <div class="email__row">
        {{ message.date | momentDateTimeShort }}
      </div>
      <div class="email__row">
        From:
        <div v-for="(contact, index) in message.from" class="email__contact-tag" :key="index">
          {{ contact.email }}
        </div>
      </div>
      <div class="email__row">
        To:
        <div v-for="(contact, index) in message.to" class="email__contact-tag" :key="index">
          {{ contact.email }}
        </div>
      </div>
    </div>
    <div style="width: 100%" v-if="isExpanded">
      <div style="width: 100%" v-html="message.body"></div>
    </div>
    <!--TODO: BREAK THIS OUT INTO ITS OWN COMPONENT-->
    <!-- ALSO, I WANT TO BE ABLE TO TOGGLE THIS ON AND OFF -->
    <h4 class="is-title">Attachments</h4>
    <div class="email__row">
      <span
        v-for="file in message.files"
        class="email__contact-tag email__contact-tag--green"
        :key="file.id"
      >
        <!-- TODO: Change this to a file-specific style -->
        <a :href="`/api/get-file/${file.id}/`" target="_blank">
          {{ file.filename }}
        </a>
      </span>
    </div>
    <div style="width: 100%" v-if="isExpanded">
      <div class="box" v-if="isExpanded"></div>
      <EmailCompose
        @emailSent="emailSent"
        :reply-message="message"
        :show-subject="false"
      ></EmailCompose>
    </div>
  </div>
</template>

<script>
import EmailCompose from '@/components/emails/EmailCompose'

export default {
  name: 'message',
  components: { EmailCompose },
  props: {
    message: {
      type: Object,
      required: true,
    },
    initiallyExpanded: {
      type: Boolean,
      required: false,
      default: false,
    },
  },
  data() {
    return {
      isExpanded: false,
    }
  },
  created() {
    this.isExpanded = this.initiallyExpanded
  },
  methods: {
    // downloadFile(file) {
    // TODO: We are no longer using this hacky mess, but I'm keeping it here just in case.
    //   Nylas.downloadFile(file.id).then(response => {
    //     const url = window.URL.createObjectURL(new Blob([response.data]))
    //     const link = document.createElement('a')
    //     link.href = url
    //     link.setAttribute('target', '_blank')
    //     link.setAttribute('download', file.filename) //or any other extension
    //     document.body.appendChild(link)
    //     link.click()
    //   })
    // },
    emailSent() {
      this.$emit('emailSent')
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/layout';
@import '@/styles/containers';
@import '@/styles/forms';
@import '@/styles/emails';
@import '@/styles/mixins/utils';
.filter-green {
  filter: invert(45%) sepia(96%) saturate(2978%) hue-rotate(123deg) brightness(92%) contrast(80%);
}
</style>
