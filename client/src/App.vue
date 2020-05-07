<template>
  <div id="app">
    <NavBar />
    <alert-alert />
    <!-- Binding a key to the full path will remount a view if
        the detail endpoint changes-->
    <div class="page-content">
      <router-view :key="$route.fullPath"></router-view>
    </div>
  </div>
</template>

<script>
import VueScrollTo from 'vue-scrollto'
import NavBar from '@/components/NavBar'

export default {
  name: 'app',
  components: {
    NavBar,
  },
  watch: {
    // When route changes, scroll to the top
    '$route.path': function watchRoutePath() {
      VueScrollTo.scrollTo('#app', 200)
    },
  },
}
</script>

<style lang="scss">
@import '@/styles/variables';

body {
  overflow-y: scroll;
  overflow-x: auto;
  margin: 0;
  min-height: 100vh;
  background-color: $off-white;
}

#app {
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
</style>
