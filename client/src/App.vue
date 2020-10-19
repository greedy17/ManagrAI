<template>
  <div id="app">
    <NavBar
      v-if="!hideNavBar"
      @update-unviewed-notif-count="updateUnviewedNotifCount"
      :unViewedCount="unviewedNotifCount"
    />
    <alert-alert />
    <!-- Binding a key to the full path will remount a view if
        the detail endpoint changes-->
    <div :class="{ 'page-content': !hideNavBar }">
      <router-view :key="$route.fullPath"></router-view>
    </div>

    <SideNavBar
      v-if="userIsLoggedIn"
      @viewed-notif="countViewed => updateUnviewedNotifCount(unviewedNotifCount - countViewed)"
    />
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'
import VueScrollTo from 'vue-scrollto'

import NavBar from '@/components/NavBar'
import SideNavBar from '@/components/navigation/SideNavBar'

const routesWithoutNavBar = ['StoryReportDetail', 'PerformanceReportDetail']

export default {
  name: 'app',
  components: {
    NavBar,
    SideNavBar,
  },
  data() {
    return {
      unviewedNotifCount: null,
    }
  },
  watch: {
    // When route changes, scroll to the top
    '$route.path': function watchRoutePath() {
      VueScrollTo.scrollTo('#app', 200)
    },
  },
  async created() {
    if (this.userIsLoggedIn) {
      this.refreshCurrentUser()
    }
  },

  methods: {
    ...mapActions(['refreshCurrentUser']),
    toggleNotifications() {
      this.$store.commit('TOGGLE_SIDE_NAV', !this.showSideNav)
    },
    updateUnviewedNotifCount(count) {
      this.unviewedNotifCount = count
    },
  },
  computed: {
    ...mapGetters(['userIsLoggedIn']),
    ...mapGetters(['showSideNav']),
    hideNavBar() {
      return routesWithoutNavBar.includes(this.$route.name)
    },
  },
}
</script>

<style lang="scss">
@import '@/styles/variables';
@import '@/styles/mixins/utils';
@import '@/styles/mixins/inputs';

body {
  overflow-y: scroll;
  overflow-x: auto;
  margin: 0;
  min-height: 100vh;
  background-color: $off-white;
}

#app {
  @include base-font-styles;
  height: inherit;
  display: flex;
  flex-flow: column;
  background-color: $off-white;
}

.page-content {
  padding: 1rem;
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
</style>
