<template>
  <div id="app">
    <NavBar ref="navbarComponent" />
    <alert-alert :top="alertTop" />
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

const oneRem = parseInt(window.getComputedStyle(document.querySelector('html')).fontSize)

export default {
  name: 'app',
  components: {
    NavBar,
  },
  data() {
    return {
      alertTop: oneRem * 0.5,
    }
  },
  watch: {
    // When route changes, scroll to the top
    '$route.path': function watchRoutePath() {
      VueScrollTo.scrollTo('#app', 200)
    },
  },
  mounted() {
    window.alert = this.$Alert.alert // NOTE(Bruno 4-23-20): this line is for testing purposes & should be removed
    document.addEventListener('scroll', this.setAlertTop)
    if (!this.setAlertTop()) {
      this.alertTop = oneRem * 0.5
    }
  },
  methods: {
    setAlertTop() {
      let nav = this.$refs.navbarComponent.$refs.nav
      let navRect = nav.getBoundingClientRect()
      let calculation = navRect.height + navRect.top
      let calculationIsValid = navRect.height >= calculation && calculation >= 0

      if (calculationIsValid) {
        this.alertTop = calculation + oneRem * 0.5
      }

      return calculationIsValid
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
