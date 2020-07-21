<template>
  <div id="app">
    <NavBar />
    <alert-alert />
    <!-- Binding a key to the full path will remount a view if
        the detail endpoint changes-->
    <div class="page-content">
      <router-view :key="$route.fullPath"></router-view>
    </div>

    <SideNavBar v-if="userIsLoggedIn" />
  </div>
</template>

<script>
import VueScrollTo from 'vue-scrollto'
import NavBar from '@/components/NavBar'
import SideNavBar from '@/components/navigation/SideNavBar'

import { mapGetters, mapState, mapActions } from 'vuex'

export default {
  name: 'app',
  components: {
    NavBar,
    SideNavBar,
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
  },
  computed: {
    ...mapGetters(['userIsLoggedIn']),
    ...mapGetters(['showSideNav']),
  },
}
</script>

<style lang="scss">
@import '@/styles/variables';
@import '@/styles/mixins/utils';

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
  flex-grow: 1;
}

.section-shadow {
  box-shadow: 0 1px 0 0 $soft-gray;
}

::-webkit-scrollbar {
  width: 0px;
}
.muted {
  opacity: 40%;
  color: #2f3035;
  font-family: inherit;
  font-weight: 300;
}
</style>
