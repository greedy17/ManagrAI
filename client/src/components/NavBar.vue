<template>
  <div>
    <nav id="nav">
      <div class="logo">
        <span class="name">managr</span>
      </div>
      <div v-if="userIsLoggedIn" class="links">
        <NavLink icon="leads" :to="'LeadsIndex'">Opportunities</NavLink>
        <NavLink icon="forecast" :to="'Forecast'">Forecast</NavLink>
        <NavLink icon="prospect" :to="'Prospect'">Accounts</NavLink>
        <NavLink icon="reports" :to="'Reports'">Reports</NavLink>
        <!-- <NavLink icon="image" to="Styles">Styles</NavLink> -->
      </div>
      <!--       <img
        v-if="userIsLoggedIn"
        src="@/assets/images/dropdown-arrow.svg"
        class="user-menu-dropdown"
        @click="toggleUserMenu"
      /> -->
      <div class="right" ref="user-menu-icon">
        <span class="right__items" @click="toggleUserMenu" ref="toggle-user-menu">
          <svg v-if="userIsLoggedIn" class="icon" viewBox="0 0 24 20">
            <use xlink:href="@/assets/images/icon-menu.svg#settings" />
          </svg>
        </span>
        <span class="right__items" @click="toggleNotifications">
          {{ unViewedCount }}
          <svg
            v-if="userIsLoggedIn"
            class="icon"
            :class="{ green: unViewedCount > 0 }"
            viewBox="0 0 16 19"
          >
            <use xlink:href="@/assets/images/notification.svg#notification" />
          </svg>
        </span>
      </div>
    </nav>

    <div v-if="showMenus.user" class="user-menu" ref="user-menu">
      <h4 @click="routeToSettings">Settings</h4>

      <h4 @click="logOut">Log Out</h4>
    </div>
  </div>
</template>

<script>
import NavLink from '@/components/NavLink'
import Notification from '@/services/notifications/'
const POLLING_INTERVAL = 10000
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
      unViewedCount: null,
    }
  },
  async created() {
    const count = await Notification.api.getUnviewedCount({})
    this.unViewedCount = count.count
  },
  mounted() {},
  destroyed() {
    clearTimeout(this.pollingTimeout)
  },

  methods: {
    async refresh(repeat) {
      clearTimeout(this.pollingTimeout)
      try {
        const count = await Notification.api.getUnviewedCount({})
        this.unViewedCount = count.count
        if (repeat) {
          this.polllingTimeout = setTimeout(async () => {
            this.refresh(POLLING_INTERVAL)
          }, repeat)
        }
      } catch (e) {
        this.apiFailing = true
        if (repeat) {
          this.pollingTimeout = setTimeout(async () => {
            this.refresh(repeat * 2)
          }, repeat * 2)
        }
      }
    },
    toggleUserMenu() {
      this.showMenus.user = !this.showMenus.user
    },
    toggleNotifications() {
      this.$store.commit('TOGGLE_SIDE_NAV', !this.showSideNav)
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
    showSideNav() {
      return this.$store.getters.showSideNav
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
  position: relative;
}

.user-menu {
  position: absolute;
  right: 4rem;
  top: auto;
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

.right {
  margin-left: auto;
  display: flex;
  flex-direction: row;
  justify-content: space-evenly;
  position: relative;
  margin-right: 1rem;
  > * {
    margin-right: 1rem;
  }
  &__items {
    border-radius: 50%;
    padding: 0.5rem;

    &:hover {
      background-color: $soft-gray;
      cursor: pointer;
    }
    &:active {
      background-color: darken($soft-gray, 5%);
    }
  }
}
.icon {
  width: 20px;
  height: 15px;
  fill: #484a6e;
}
.icon.green {
  fill: green;
}
</style>
