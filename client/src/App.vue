<template>
  <div id="app">
    <NavBar v-if="!hideNavBar && userIsLoggedIn" />
    <!-- <alert-alert /> -->
    <!-- Binding a key to the full path will remount a view if
        the detail endpoint changes-->
    <div :class="{ 'page-content': !hideNavBar }">
      <router-view :key="$route.fullPath"></router-view>
    </div>
    <!-- <img src="@/assets/images/backgroundLogo.png" class="background-logo" /> -->
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'
import VueScrollTo from 'vue-scrollto'

import NavBar from '@/components/NavBar'

const routesWithoutNavBar = ['StoryReportDetail', 'PerformanceReportDetail']

export default {
  name: 'app',
  components: {
    NavBar,
  },
  data() {
    return {
      
    }
  },
  watch: {
    // When route changes,
    '$route.path': function watchRoutePath() {
      const newDateTime = Date.now()
      // If it's been more than an hour,
      if (newDateTime - localStorage.dateTime > 3600000) {
        // Log out
        if (localStorage.isLoggedOut) {
          return
        } else {
          localStorage.isLoggedOut = true
          this.$store.dispatch('logoutUser')
          this.$router.push({ name: 'Login' })
        }
      } else {
        // reset localStorage datetime
        localStorage.dateTime = newDateTime
        // scroll to the top
        VueScrollTo.scrollTo('#app', 200)
      }
    },
  },
  async created() {
    if (this.userIsLoggedIn) {
      this.refreshCurrentUser()
    }
    this.$store.dispatch('loadMeetings')
    this.$store.dispatch('loadAllOpps')
    this.$store.dispatch('loadAllAccounts')
    this.$store.dispatch('loadAllContacts')
    this.$store.dispatch('loadAllPicklists')
    this.$store.dispatch('loadApiPicklists')
    this.$store.dispatch('loadPricebooks')
    this.$store.dispatch('loadTemplates')
    if (this.$store.state.user.crm === 'SALESFORCE') {
      this.$store.dispatch('getRecords')
      this.$store.dispatch('loadAllLeads')
    }
    // this.$store.dispatch('loadWorkflows')
  },

  methods: {
    ...mapActions(['refreshCurrentUser']),
  },
  computed: {
    ...mapGetters(['userIsLoggedIn']),
    hideNavBar() {
      return routesWithoutNavBar.includes(this.$route.name)
    },
    userIsLoggedIn() {
      return this.$store.getters.userIsLoggedIn
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

.page-content {
  padding: 2px 16px;
}

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
</style>
