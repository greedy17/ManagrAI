<template>
  <nav>
    <div class="logo">
      <span class="name">
        managr
      </span>
    </div>
    <div v-if="userIsLoggedIn" class="links">
      <NavLink icon="leads" :to="'LeadsIndex'">Leads</NavLink>
      <NavLink icon="prospect" :to="'Prospects'">Prospect</NavLink>
      <NavLink icon="forecast" :to="'Forecast'">Forecast</NavLink>
      <NavLink icon="reports" :to="'Reports'">Reports</NavLink>
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

export default {
  name: 'NavBar',
  components: {
    NavLink,
  },
  computed: {
    userIsLoggedIn() {
      return this.$store.getters.userIsLoggedIn
    },
  },
}
</script>

<style lang="scss" scoped>
@import url('https://fonts.googleapis.com/css2?family=Quicksand&display=swap');
@import '@/styles/variables';
@import '@/styles/mixins/utils';

nav {
  height: 63px;
  display: flex;
  flex-flow: row;
  align-items: center;
  background-color: #ffffff;
}

.logo {
  @include disable-text-select();
  margin-left: 25px;
  display: flex;
  align-items: center;

  .image {
    width: 40px;
    height: 40px;
  }

  .name {
    display: flex;
    align-items: center;
    font-family: $logo-font-family;
    font-size: 36px;
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
