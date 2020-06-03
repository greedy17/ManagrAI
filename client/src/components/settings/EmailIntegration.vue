<template>
  <div class="container">
    <div class="box">
      <div class="box__header">
        <div class="box__title">Email Integration</div>
      </div>
      <div class="box__content">
        <div class="flexbox-container v-centered">
          <div>
            <a :href="user.emailAuthLink" style="text-decoration: none">
              <button
                class="inactive-button "
                v-if="!user.emailAuthAccount || !user.emailAuthAccountRef.accessToken"
              >
                Connect Email
              </button>
            </a>
            <button
              class="primary-button"
              style="margin-bottom: .1rem;"
              v-if="user.emailAuthAccount && user.emailAuthAccountRef.accessToken"
            >
              Connected
            </button>
            <div
              class="disconnect"
              v-if="user.emailAuthAccount && user.emailAuthAccountRef.accessToken"
              @click="revokeToken"
            >
              X Disconnect
            </div>
          </div>
          <div>
            Sync <strong>{{ user.email }}</strong> with your Managr Account
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex'
import Nylas from '@/services/nylas'
import Thread from '@/components/emails/Thread'

export default {
  name: 'EmailIntegration',
  components: { Thread },
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
      Nylas.getUserThreads(this.filterBy).then(response => {
        this.threads = response.data
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
  text-align: right;
  font-size: 12px;
  margin: 0 0.5rem 0 0;
  color: $coral;
}

.v-centered {
  align-items: center;
}
</style>
