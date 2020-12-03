<template>
  <div class="container">
    <div class="box">
      <div class="box__tab-header">
        <div class="box__tab">Text</div>
        <div class="box__tab--active">Emails</div>
        <div class="box__tab">Notes</div>
        <div class="box__tab">Reminders</div>
      </div>
      <div class="box__content">
        <EmailCompose />
      </div>
    </div>
    <button class="button" @click="refreshEmails">
      Refresh Emails
    </button>
    <div class="box">
      <div class="actions__container">
        <div class="actions__item actions__container--header ">
          <div class="actions__row">
            <div class="actions__item-header-icon"></div>
            <div class="actions__item-header-title">Additional Information</div>
            <div class="actions__item-header-date">Date</div>
            <div class="actions__item-header-action"></div>
          </div>
        </div>
        <div v-if="isLoading" style="padding: 5rem;">
          <ComponentLoadingSVG v-if="isLoading" />
        </div>
        <Thread
          @email-sent="refreshEmails"
          :thread="thread"
          v-for="thread in threads"
          :key="thread.id"
        ></Thread>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex'
import Nylas from '@/services/nylas'
import Thread from '@/components/emails/Thread'
import ComponentLoadingSVG from '@/components/ComponentLoadingSVG'
import EmailCompose from '@/components/emails/EmailCompose'

export default {
  name: 'Profile',
  components: { Thread, EmailCompose, ComponentLoadingSVG },
  data() {
    return {
      threads: [],
      isLoading: false,
    }
  },
  computed: {
    ...mapState(['user']),
  },
  methods: {
    refreshEmails() {
      this.isLoading = true
      Nylas.getThreads({ toEmail: this.filterBy })
        .then(data => {
          this.threads = data
        })
        .finally(() => {
          this.isLoading = false
        })
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
@import '@/styles/sidebars';
</style>
