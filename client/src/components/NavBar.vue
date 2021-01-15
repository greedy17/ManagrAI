<template>
  <div>
    <nav id="nav">
      <div class="logo">
        <img src="@/assets/images/logo-with-name.png" />
      </div>
      <div v-if="userIsLoggedIn" class="links">
        <NavLink icon="leads" :to="'LeadsIndex'">Opportunities</NavLink>
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
      </div>
    </nav>
  </div>
</template>

<script>
import NavLink from '@/components/NavLink'

import DropDownMenu from '@/components/forms/DropDownMenu'

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
  async created() {},
  mounted() {},
  destroyed() {},

  methods: {
    routeToSelected(selected) {
      if (selected == 'settings') {
        this.routeToSettings()
      }
      if (selected == 'logout') {
        this.logOut()
      }
    },

    routeToSettings() {
      this.$router.push({ name: 'EmailIntegration' })
      this.toggleUserMenu()
    },
    logOut() {
      this.$store.dispatch('logoutUser')
      this.$router.push({ name: 'Login' })
      this.$store.commit('CLEAR_POLLING_DATA')
      this.toggleUserMenu()
    },
  },
  watch: {},
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
