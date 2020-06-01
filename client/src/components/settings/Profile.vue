<template>
  <div class="container">
    <div class="box">
      <div class="box__tab-header">
        <div class="box__tab">Text</div>
        <div class="box__tab--active">Emails</div>
        <div class="box__tab">Blah</div>
        <div class="box__tab">Notes</div>
        <div class="box__tab">Reminders</div>
      </div>
      <div class="box__content">
        New Email Form goes Here
      </div>
    </div>
    <button class="button" @click="refreshEmails">
      Refresh Emails
    </button>
    <div class="box">
      <div class="actions__container">
        <div class="actions__item actions__container--header ">
          <div class="actions__item-header">
            <div class="actions__item-header-icon"></div>
            <div class="actions__item-header-title">Additional Information</div>
            <div class="actions__item-header-date">Date</div>
            <div class="actions__item-header-action"></div>
          </div>
        </div>

        <!-- EMAIL COMPONENT STARTS HERE -->
        <Thread :thread="thread" v-for="thread in threads" :key="thread.id"></Thread>
      </div>
    </div>
  </div>
</template>

<script>
import Nylas from '@/services/nylas'
import Thread from '@/components/emails/Thread'

export default {
  name: 'Profile',
  components: { Thread },
  data() {
    return {
      threads: [],
    }
  },
  methods: {
    refreshEmails() {
      Nylas.getUserThreads(this.filterBy).then(response => {
        this.threads = response.data
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
</style>
