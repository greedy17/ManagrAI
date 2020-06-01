<template>
  <nav id="nav">
    <div class="logo">
      <span class="name">managr</span>
    </div>
    <div v-if="userIsLoggedIn" class="links">
      <NavLink icon="leads" :to="'LeadsIndex'">Leads</NavLink>
      <NavLink icon="forecast" :to="'Forecast'">Forecast</NavLink>
      <NavLink icon="prospect" :to="'Prospect'">Prospect</NavLink>
      <NavLink icon="reports" :to="'Reports'">Reports</NavLink>
      <NavLink icon="leads" to="Settings">Settings</NavLink>
      <a style="padding-top: 20px;" @click="logOut">Log Out</a>
    </div>
    <img
      v-if="userIsLoggedIn"
      src="@/assets/images/screenshots/navbar-search-and-profile.png"
      alt="screenshot"
      class="navbar-search-and-profile"
    />
  </nav>
</template>

<script>
import NavLink from '@/components/NavLink'
import { mapActions } from 'vuex'

export default {
  name: 'NavBar',
  components: {
    NavLink,
  },
  methods: {
    logOut() {
      this.$store.dispatch('logoutUser')
      this.$router.push({ name: 'Login' })
    },
  },
  computed: {
    userIsLoggedIn() {
      return this.$store.getters.userIsLoggedIn
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/utils';

nav {
  height: 4rem;
  display: flex;
  flex-flow: row;
  align-items: center;
  background-color: $white;
  border-bottom: 1px solid $soft-gray;
}

.logo {
  @include disable-text-select();
  margin-left: 1.5rem;
  display: flex;
  align-items: center;

  .image {
    width: 2.5rem;
    height: 2.5rem;
  }

  .name {
    display: flex;
    align-items: center;
    font-family: $logo-font-family;
    font-size: 2.25rem;
    font-weight: 500;
    font-stretch: normal;
    font-style: normal;
    line-height: normal;
    color: $dark-green;
  }
}

.links {
  display: flex;
  flex-flow: row;
  margin-left: 26%;
  width: 28%;
}

.navbar-search-and-profile {
  height: 34px;
  margin-left: auto;
  margin-right: 34px;
}
</style>
