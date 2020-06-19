<template>
  <div>
    <nav id="nav">
      <div class="logo">
        <span class="name">managr</span>
      </div>
      <div v-if="userIsLoggedIn" class="links">
        <NavLink icon="leads" :to="'LeadsIndex'">Leads</NavLink>
        <NavLink icon="forecast" :to="'Forecast'">Forecast</NavLink>
        <NavLink icon="prospect" :to="'Prospect'">Accounts</NavLink>
        <NavLink icon="reports" :to="'Reports'">Reports</NavLink>
        <!-- <NavLink icon="image" to="Styles">Styles</NavLink> -->
      </div>
      <img
        v-if="userIsLoggedIn"
        src="@/assets/images/dropdown-arrow.svg"
        class="user-menu-dropdown"
        @click="toggleUserMenu"
      />
    </nav>
    <div class="menu-container">
      <div v-if="showMenus.user" class="user-menu-container">
        <div class="user-menu">
          <h4 @click="routeToSettings">Settings</h4>
          <h4 @click="logOut">Log Out</h4>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import NavLink from '@/components/NavLink'

export default {
  name: 'NavBar',
  components: {
    NavLink,
  },
  data() {
    return {
      showMenus: {
        user: false,
      },
    }
  },
  methods: {
    toggleUserMenu() {
      this.showMenus.user = !this.showMenus.user
    },
    routeToSettings() {
      this.$router.push({ name: 'Settings' })
      this.toggleUserMenu()
    },
    logOut() {
      this.$store.dispatch('logoutUser')
      this.$router.push({ name: 'Login' })
      this.toggleUserMenu()
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

.user-menu-dropdown {
  margin-left: auto;
  margin-right: 1rem;
  opacity: 0.6;
}

.menu-container {
  z-index: 1000;
  position: absolute;
  width: 100%;
  display: flex;
  flex-flow: column;
}

.user-menu-container {
  display: flex;
  flex-flow: row;
  justify-content: right;

  .user-menu {
    @include standard-border;
    border-top: 0px;
    box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.05);
    background-color: $white;
    margin-left: auto;
    margin-right: 1vw;
    min-width: 7rem;
    padding-left: 1rem;

    h4 {
      @include pointer-on-hover;
      @include disable-text-select;
    }
  }
}
</style>
