<template>
  <div class="container">
    <div class="box">
      <div class="box__header">
        <div class="box__title">Email Integration</div>
      </div>

      <!-- Email integration NOT ACTIVE -->
      <div class="box__content" v-if="!user.emailConnected">
        <div>
          <strong>{{ user.email }}</strong> is not yet synced with your Managr account.
        </div>
        <div style="margin: 1rem 0">
          <a :href="user.emailAuthLink" style="text-decoration: none">
            <button class="inactive-button">Connect Email</button>
          </a>
        </div>
      </div>

      <!-- Email integration active -->
      <div class="box__content" v-if="user.emailConnected">
        <div>
          <strong>{{ user.email }}</strong> is synced with your Mangr account.
        </div>
        <div style="margin: 1rem 0">
          <button class="disconnect" v-if="user.emailConnected" @click="revokeToken">
            × Disconnect
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex'
import Nylas from '@/services/nylas'

export default {
  name: 'EmailIntegration',
  data() {
    return {
      filterBy: '',
      loading: true,
      emailsLoaded: false,
      threads: [],
    }
  },
  methods: {
    ...mapActions(['refreshCurrentUser']),
    revokeToken() {
      Nylas.revokeUserToken()
        .then(() => {
          this.refreshCurrentUser()
        })
        .then(() => {
          this.$Alert.alert({
            type: 'success',
            timeout: 4000,
            message: 'Email Disconnected',
          })
        })
    },
    refreshEmails() {
      Nylas.getThreads({ toEmail: this.filterBy }).then(data => {
        this.threads = data
      })
    },
  },
  computed: {
    ...mapState(['user']),
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/mixins/buttons';
@import '@/styles/forms';
@import '@/styles/variables';
@import '@/styles/containers';
@import '@/styles/layout';

.disconnect {
  @include button-danger;
}

.v-centered {
  align-items: center;
}
</style>
