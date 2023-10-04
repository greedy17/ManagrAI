<template>
  <div id="app">
    <Modal v-if="showExpireModal" class="delete-modal">
      <div class="delete-container">
        <header>
          <p>X</p>
        </header>
        <main>
          <h2>Session Expiring</h2>
          <p>Are you still using Managr ?</p>

          <div style="margin-top: 20px" class="row">
            <button @click="logOut" class="tertiary-button">No</button>
            <button @click="refreshToken" class="primary-button">Yes</button>
          </div>
        </main>
      </div>
    </Modal>
    <NavBar
      v-if="!hideNavBar && userIsLoggedIn"
      :menuOpen="menuOpen"
      @toggle-menu="toggleMenu"
      @close-menu="closeMenu"
    />
    <!-- <alert-alert /> -->
    <!-- Binding a key to the full path will remount a view if
        the detail endpoint changes-->
    <div :class="{ 'page-content': !hideNavBar }">
      <router-view :key="$route.fullPath"></router-view>
    </div>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'
import VueScrollTo from 'vue-scrollto'
import User from '@/services/users'
import NavBar from '@/components/NavBar'
import { decryptData } from './encryption'

const routesWithoutNavBar = ['StoryReportDetail', 'PerformanceReportDetail', 'Home']

export default {
  name: 'app',
  components: {
    NavBar,
    Modal: () => import(/* webpackPrefetch: true */ '@/components/InviteModal'),
  },
  data() {
    return {
      menuOpen: false,
      showExpireModal: false,
      checkInterval: null,
    }
  },
  watch: {
    timeUntilExpiry: 'handleLogoutRefresh',
    // When route changes,
    '$route.path': function watchRoutePath() {
      VueScrollTo.scrollTo('#app', 200)
      this.checkTokenExpiry()
      if (localStorage.token && !this.$store.state.token) {
        this.$store.dispatch('updateUserToken', localStorage.token)
      }
      // if (this.userIsLoggedIn) {
      //   if (this.isOnboarding && this.user.isAdmin && this.$route.path !== '/alerts/list-templates') {
      //     this.$router.push({ name: 'ListTemplates' })
      //   }
      //   const newDateTime = Date.now()
      //   // If it's been more than an hour,
      //   if (newDateTime - localStorage.dateTime > 3600000) {
      //     // Log out
      //     if (localStorage.isLoggedOut) {
      //       return
      //     } else {
      //       localStorage.isLoggedOut = true
      //       this.$store.dispatch('logoutUser')
      //       this.$router.push({ name: 'Login' })
      //     }
      //   } else {
      //     // reset localStorage datetime
      //     localStorage.dateTime = newDateTime
      //     // scroll to the top
      //     VueScrollTo.scrollTo('#app', 200)
      //   }
      // }
    },
  },

  async created() {
    this.checkInterval = setInterval(this.checkTokenExpiry, 60000)
    if (this.userIsLoggedIn) {
      this.refreshCurrentUser()
      if (this.$store.state.selectedArticle === null) {
        // change this to be the actual first article
        const article = {}
        this.$store.dispatch('updateSelectedArticle', article)
      }
    } else {
      // this.$router.push({ name: 'Login' })
    }
  },

  beforeDestroy() {
    clearInterval(this.checkInterval)
  },

  methods: {
    ...mapActions(['refreshCurrentUser']),
    openModal() {
      this.modalOpen = true
    },
    closeModal() {
      this.modalOpen = false
    },
    toggleMenu() {
      this.menuOpen = !this.menuOpen
    },
    closeMenu() {
      this.menuOpen = false
    },
    checkTokenExpiry() {
      if (localStorage.getItem('tokenReceivedAt')) {
        const tokenReceivedAt = new Date(parseInt(localStorage.getItem('tokenReceivedAt')))
        const expiresAt = new Date(tokenReceivedAt.getTime() + 14400000)
        const currentTime = new Date()

        if (currentTime >= new Date(expiresAt.getTime() - 300000)) {
          this.showExpiryWarning()
        }

        if (currentTime >= expiresAt) {
          clearInterval(this.checkInterval)
          this.logOut()
        }
      } else {
        return
      }
    },
    showExpiryWarning() {
      this.showExpireModal = true
    },
    logOut() {
      this.showExpireModal = false
      localStorage.removeItem('token')
      localStorage.removeItem('tokenReceivedAt')
      this.$store.dispatch('logoutUser')
      this.$router.push({ name: 'Login' })
    },
    async refreshToken() {
      try {
        await User.api
          .refreshToken(localStorage.getItem('token'), this.user.id)
          .then((response) => {
            console.log('TOKEN RESPONSE', response)
            clearInterval(this.checkInterval)
            let token = response.data.token
            localStorage.setItem('token', token)
            this.$store.dispatch('updateUserToken', token)
            localStorage.setItem('tokenReceivedAt', Date.now().toString())
            this.checkTokenExpiry()
            this.checkInterval = setInterval(this.checkTokenExpiry, 60 * 1000)
          })
      } catch (e) {
        console.log(e)
      } finally {
        this.showExpireModal = false
      }
    },
  },
  computed: {
    ...mapGetters(['userIsLoggedIn']),
    hideNavBar() {
      return routesWithoutNavBar.includes(this.$route.name)
    },
    userIsLoggedIn() {
      return this.$store.getters.userIsLoggedIn
    },
    isOnboarding() {
      // const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
      return this.$store.state.user.onboarding
    },
    user() {
      // const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
      return this.$store.state.user
    },
  },
}
</script>

<style lang="scss">
// Include global variables and styles here
@import '@/styles/variables';
@import '@/styles/buttons';
@import '@/styles/cards';
@import '@/styles/mixins/utils';
@import '@/styles/mixins/inputs';
.Vue-Toastification__toast--success.custom {
  background-color: $dark-green;
}
.Vue-Toastification__toast--default.custom {
  background-color: $base-gray;
}
* {
  box-sizing: border-box;
}

body {
  overflow: auto;
  margin: 0;
  //  margin: 0 1rem 0 1rem;
  min-height: 100vh;
  background-color: $off-white;
}

div[id^='user-input'] {
  // display: none;
  outline: 1px solid yellow !important;
}

input {
  background-image: none !important;
}

#app {
  @include base-font-styles;
  height: inherit;
  display: flex;
  flex-flow: column;
}

// .page-content {
//   padding: 2px 16px;
// }

::-webkit-scrollbar {
  width: 0px;
}

.background-logo {
  position: absolute;
  top: 40%;
  right: 0rem;
  height: 60vh;
  width: 50vw;
  z-index: -1;
}

.delete-modal {
  margin-top: 120px;
  width: 100%;
  height: 100%;
}

.delete-container {
  width: 500px;
  height: 220px;
  color: $base-gray;
  font-family: $thin-font-family;
  font-size: 14px;
  line-height: 24px;
  font-weight: 400;

  header {
    display: flex;
    flex-direction: row;
    justify-content: flex-end;

    p {
      cursor: pointer;
      margin-top: -4px;
    }
  }

  main {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;

    // h2 {
    //   margin-bottom: 0px;
    // }
  }
}

.row {
  display: flex;
  align-items: center;
  flex-direction: row;
}

.tertiary-button {
  @include dark-blue-button();
  padding: 6px 10px;
  border: 1px solid rgba(0, 0, 0, 0.2);
  color: $dark-black-blue;
  background-color: white;
  margin-right: -2px;
  display: flex;
  flex-direction: row;
  align-items: center;
}

.primary-button {
  @include dark-blue-button();
  padding: 6px 10px;
  margin-left: 16px;
}
</style>
