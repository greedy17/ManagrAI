<template>
  <div>
    <div style="padding: 25px">
      <h3>OAuth Integration</h3>
      <h4>Email Connection</h4>
      <img
        v-if="user.emailAuthLink && user.emailAuthLink.accessToken"
        alt="icon"
        :src="require(`@/assets/images/checkmark.svg`)"
        class="icon"
      />
      <img
        v-if="user.emailAuthLink && !user.emailAuthLink.accessToken"
        alt="icon"
        :src="require(`@/assets/images/remove.svg`)"
        class="icon"
      />
      <hr />
      <input v-model="email" />

      <br />
      <button>Connect Email</button>
      <br />
      <a v-if="authUrl" :href="authUrl">Click Here to Connect</a>
      <hr />
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
  </div>
</template>

<script>
import { mapState } from 'vuex'
import User from '@/services/users'
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
    this.getNylasEmailLink()
    this.refreshEmails()
  },
  methods: {
    refreshEmails() {
      this.emailsLoading = true
      Nylas.getUserThreads(this.filterBy).then(response => {
        this.threads = response.data
        this.emailsLoading = false
      })
    },
    getNylasEmailLink() {
      let emailPromise = User.api.getNylasEmailLink()
      emailPromise.then(response => {
        this.authUrl = response.data.email_auth_link
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
