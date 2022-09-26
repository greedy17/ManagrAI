<template>
  <div id="app">
    <NavBar v-if="!hideNavBar && userIsLoggedIn" />
    <!-- <SideDrawer :key="$route.fullPath"></SideDrawer> -->
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
import SideDrawer from '@/components/SideDrawer'

const routesWithoutNavBar = ['StoryReportDetail', 'PerformanceReportDetail']

export default {
  name: 'app',
  components: {
    NavBar,
    SideDrawer,
  },
  data() {
    return {
      unviewedNotifCount: null,
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

.section-shadow {
  box-shadow: 0 1px 0 0 $soft-gray;
}

::-webkit-scrollbar {
  width: 0px;
}

.muted {
  color: rgba(47, 48, 53, 0.4);
  font-family: inherit;
  font-weight: 300;
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
