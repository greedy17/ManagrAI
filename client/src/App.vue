<template>
  <div id="app">
    <!-- Binding a key to the full path will remount a view if
        the detail endpoint changes-->
    <router-view :key="$route.fullPath"></router-view>
  </div>
</template>

<script>
import VueScrollTo from 'vue-scrollto'

export default {
  name: 'app',
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
  margin: 0px;
  height: 100vh;
  background-color: $off-white;
}

#app {
  height: inherit;
}

/* for development purposes */
// div {
//   border-style: dashed;
//   border-width: 1px;
// }
</style>
