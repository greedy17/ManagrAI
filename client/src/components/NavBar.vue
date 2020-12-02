<template>
  <div>
    <nav id="nav">
      <div class="logo" @click="goToHome">
        <img src="@/assets/images/logo-with-name.png" />
      </div>
      <div v-if="userIsLoggedIn" class="links">
        <NavLink icon="leads" :to="'LeadsIndex'">Opportunities</NavLink>
        <NavLink icon="forecast2" :to="'Forecast'">Forecast + Deals</NavLink>
        <NavLink icon="prospect" :to="'Prospect'">Accounts</NavLink>
        <NavLink icon="reports" :to="'Reports'">Reports</NavLink>
        <NavLink icon="zoom" to="Meetings">Meetings</NavLink>
        <!-- <NavLink icon="image" to="Styles">Styles</NavLink> -->
      </div>

      <div class="right" ref="user-menu-icon">
        <div v-if="userIsLoggedIn" class="right__items">
          <DropDownMenu
            @selectedItem="routeToSelected"
            :right="10"
            :items="[
              { key: 'Settings', value: 'settings' },
              { key: 'Log Out', value: 'logout' },
            ]"
          >
            <template v-slot:dropdown-trigger="{ toggle }">
              <svg ref="dd-user-settings" @click="toggle" class="dd-icon" viewBox="0 0 24 20">
                <use xlink:href="@/assets/images/icon-menu.svg#settings" />
              </svg>
            </template>
          </DropDownMenu>
        </div>

        <span
          v-if="userIsLoggedIn"
          ref="notification-trigger"
          class="right__items"
          @click.prevent="toggleNotifications"
        >
          {{ unViewedCount > 0 ? unViewedCount : '' }}
          <svg
            v-if="userIsLoggedIn"
            class="icon"
            :class="{ green: unViewedCount > 0 }"
            viewBox="0 0 16 19"
          >
            <use
              ref="notification-trigger"
              xlink:href="@/assets/images/notification.svg#notification"
            />
          </svg>
        </span>
      </div>
    </nav>
  </div>
</template>

<script>
import NavLink from '@/components/NavLink'
import Notification from '@/services/notifications/'
import DropDownMenu from '@/components/forms/DropDownMenu'

const POLLING_INTERVAL = 10000

export default {
  name: 'NavBar',
  components: {
    NavLink,
    DropDownMenu,
  },
  props: {
    unViewedCount: {
      required: true,
    },
  },
  data() {
    return {
      showMenus: {
        user: false,
      },
    }
  },
  async created() {
    if (this.userIsLoggedIn) {
      const { count } = await Notification.api.getUnviewedCount({})
      this.$emit('update-unviewed-notif-count', count)
      this.$store.commit('UPDATE_ITEMS_TO_POLL', 'notification')
      this.$store.commit('UPDATE_ITEMS_TO_POLL', 'notificationCount')

      await this.refresh(POLLING_INTERVAL)
    }
  },
  mounted() {},
  destroyed() {
    clearTimeout(this.pollingTimeout)
  },

  methods: {
    routeToSelected(selected) {
      // TODO: PB Change this to be static with an enum type list (django style) 07/20
      if (selected == 'settings') {
        this.routeToSettings()
      }
      if (selected == 'logout') {
        this.logOut()
      }
    },
    async refresh(repeat) {
      clearTimeout(this.pollingTimeout)
      try {
        await this.$store.dispatch('updatePollingData')

        if (repeat) {
          this.polllingTimeout = setTimeout(async () => {
            await this.refresh(POLLING_INTERVAL)
          }, repeat)
        }
      } catch (e) {
        this.apiFailing = true
        if (repeat) {
          this.pollingTimeout = setTimeout(async () => {
            await this.refresh(repeat * 2)
          }, repeat * 2)
        }
      }
    },

    toggleUserMenu() {
      this.showMenus.user = !this.showMenus.user
      if (this.showMenus.user) {
        this.$store.commit('TOGGLE_SIDE_NAV', false)
      }
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
      this.$store.commit('CLEAR_POLLING_DATA')
      this.toggleUserMenu()
    },
    goToHome() {
      if (this.$route.name !== 'LeadsIndex') {
        this.$router.push({ name: 'LeadsIndex' })
      }
    },
  },
  watch: {
    shouldRefreshPolling(val) {
      if (val) {
        if (this.$store.getters.pollingDataToUpdate.includes('notificationCount')) {
          let count = this.$store.state.pollingData.items.notificationCount.count
          this.$emit('update-unviewed-notif-count', count)
        }
      }
    },
  },
  computed: {
    shouldRefreshPolling() {
      return this.$store.getters.updatePollingData
    },
    itemsToRefresh() {
      return this.$store.getters.pollingDataToUpdate
    },
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
  height: 4.5rem;
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

  &:hover {
    cursor: pointer;
  }

  img {
    height: 10rem;
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
  z-index: 100;

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
.dd-icon {
  width: 20px;
  height: 15px;
  fill: #484a6e;
}
</style>
