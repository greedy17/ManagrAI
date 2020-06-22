<template>
  <div>
    <div>
      <h3>Filter By Email</h3>
      <input type="text" v-model="filterBy" />
      <button @click="refreshEmails">Refresh Emails</button>
      <h3>Email Sample</h3>
      <h4>Thread</h4>
      <div v-if="emailsLoading">
        Loading...
      </div>
      <div v-if="!emailsLoading">
        <Thread :thread="thread" v-for="thread in threads" :key="thread.id" />
      </div>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex'
import Nylas from '@/services/nylas'
import Thread from '@/components/emails/Thread'

export default {
  name: 'Nylas',
  components: { Thread },
  data() {
    return {
      filterBy: '',
      email: '',
      loading: false,
      authUrl: '',
      threads: {},
      emailsLoading: false,
    }
  },
  created() {
    this.refreshEmails()
  },
  methods: {
    refreshEmails() {
      this.emailsLoading = true
      Nylas.getThreads({ toEmail: this.filterBy }).then(data => {
        this.threads = data
        this.emailsLoading = false
      })
    },
  },
  computed: {
    ...mapState(['user']),
    isCurrentRoute() {
      return this.$route.name == 'Nylas'
    },
  },
}
</script>

<style lang="scss" scoped></style>
