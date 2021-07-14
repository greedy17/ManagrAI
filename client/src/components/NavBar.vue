<template>
  <div>
    <nav id="nav" v-if="userIsLoggedIn">
      <div class="logo">
        <img src="@/assets/images/logo-with-name.png" />
      </div>

      <div class="left" ref="user-menu-icon">
        <div class="mar" v-if="isAdmin">
          <ul>
            <li>
              <router-link exact-active-class="active" :to="{ name: 'Integrations' }"
                >Integrations
              </router-link>
            </li>
            <li>
              <router-link exact-active-class="active" :to="{ name: 'SlackFormSettings' }"
                >Form Builder
              </router-link>
            </li>
            <li>
              <router-link exact-active-class="active" :to="{ name: 'CreateNew' }"
                >Smart Alerts
              </router-link>
            </li>
            <li>
              <router-link exact-active-class="active" :to="{ name: 'InviteUsers' }"
                >Invite Users</router-link
              >
            </li>
          </ul>
        </div>

        <div class="mar" v-if="!isAdmin">
          <ul>
            <li>
              <router-link :to="{ name: 'Integrations' }">Integrations </router-link>
            </li>
          </ul>
        </div>

        <!-- <DropDownMenu
            @selectedItem="routeToSelected"
            :right="10"
            :items="[
              { key: 'Integrations', value: 'Integrations' },
              { key: 'Slack Forms', value: 'SlackFormSettings' },
              { key: 'Invite Users', value: 'InviteUsers' },
              { key: 'Smart Alerts (Beta)', value: 'CreateNew' },
              { key: 'Profile', value: 'ProfilePage' },
              { key: 'Log Out', value: 'logout' },
            ]"
            v-if="isAdmin"
          >
            <template v-slot:dropdown-trigger="{ toggle }">
              <svg ref="dd-user-settings" @click="toggle" class="dd-icon" viewBox="-5 0 24 18">
                <use xlink:href="@/assets/images/icon-menu.svg#settings" />
              </svg>
            </template>
          </DropDownMenu>

          <DropDownMenu
            @selectedItem="routeToSelected"
            :right="10"
            :items="[
              { key: 'Integrations', value: 'Integrations' },
              { key: 'Profile', value: 'ProfilePage' },
              { key: 'Log Out', value: 'logout' },
            ]"
            v-if="!isAdmin"
          >
            <template v-slot:dropdown-trigger="{ toggle }">
              <svg ref="dd-user-settings" @click="toggle" class="dd-icon" viewBox="-5 0 24 18">
                <use xlink:href="@/assets/images/icon-menu.svg#settings" />
              </svg>
            </template>
          </DropDownMenu> -->
      </div>

      <div class="right">
        <img
          src="@/assets/images/toolTip.png"
          class="tooltip__icon"
          @mouseover="toggleTooltip"
          @mouseleave="toggleTooltip"
        />
        <div class="tooltip__popup" v-if="tooltipOpen">
          <div class="tooltip__popup__bold">Having issues?</div>
          <div>Email support@mymanagr.com</div>
        </div>

        <div class="profile">
          <router-link style="color: #199e54" :to="{ name: 'ProfilePage' }">{{
            userInitials
          }}</router-link>
        </div>

        <div>
          <router-link :to="{ name: 'Login' }"
            ><img @click="logOut" src="@/assets/images/logout.png" alt="" style="height: 1.5rem"
          /></router-link>
        </div>
      </div>
    </nav>
  </div>
</template>

<script>
import DropDownMenu from '@/components/forms/DropDownMenu'

export default {
  name: 'NavBar',
  components: {
    DropDownMenu,
  },
  props: {},
  data() {
    return {
      showMenus: {
        user: false,
      },
      items: [],
      tooltipOpen: false,
      dropdownOpen: false,
      userInitials: this.$store.state.user.firstName[0] + this.$store.state.user.lastName[0],
    }
  },

  async created() {
    if (this.isAdmin) {
      this.items = [
        { key: 'Integrations', value: 'Integrations' },
        { key: 'Slack Forms', value: 'SlackFormSettings' },
        { key: 'Invite Users', value: 'InviteUsers' },
        { key: 'Log Out', value: 'logout' },
      ]
    } else {
      this.items = [
        { key: 'Integrations', value: 'Integrations' },
        { key: 'Log Out', value: 'logout' },
      ]
    }
  },
  mounted() {},
  destroyed() {},

  methods: {
    toggleDropDown() {
      this.dropdownOpen = !this.dropdownOpen
    },
    toggleTooltip() {
      this.tooltipOpen = !this.tooltipOpen
    },
    routeToSelected(selected) {
      if (selected == 'logout') {
        this.logOut()
      } else {
        this.$router.push({ name: selected })
      }
    },

    routeToSettings() {
      this.$router.push({ name: 'Integrations' })
    },
    logOut() {
      this.$store.dispatch('logoutUser')
      this.$router.push({ name: 'Login' })
    },
  },
  watch: {},
  computed: {
    userIsLoggedIn() {
      return this.$store.getters.userIsLoggedIn
    },
    isAdmin() {
      return this.userIsLoggedIn && this.$store.state.user.isAdmin
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
  margin-right: 2rem;
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
  align-items: center;
  justify-content: center;
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
.left {
  margin-right: auto;
  display: flex;
  flex-direction: row;
  justify-content: space-evenly;
  position: relative;
  margin-right: 1rem;
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

.tooltip {
  position: relative;
  &__icon {
    width: 18px;
    margin-top: 1rem;
    &:hover {
      cursor: pointer;
    }
  }

  &__popup {
    width: 20rem;

    margin: 2px 13px 3px 40px;
    padding: 13px 21px 16px 29px;
    border-radius: 5px;
    box-shadow: 0 5px 10px 0 rgba(0, 0, 0, 0.2);
    border: solid 2px #dcdddf;
    background-color: #ffffff;
    position: absolute;
    right: 4rem;

    &__bold {
      font-family: #{$bold-font-family};
    }
  }
}

ul {
  list-style-type: none;
  margin: 0;
  padding: 0;
}

li {
  display: inline;
  padding: 1rem;
  text-align: center;
  font-weight: bold;
  margin-top: 1rem;
}
.profile {
  border: 3px solid $dark-green;
  border-radius: 50%;
  font-size: 12px;
  font-weight: bold;
  padding: 0.25rem;
  margin-top: 1rem;
  margin-right: 1rem;
}
img {
  margin-top: 1rem;
}
a {
  text-decoration: none;
  color: $night-rider;
}

a:hover {
  color: $dark-green;
}
.mar {
  margin-top: 1rem;
}
.active {
  border-bottom: 3px solid $dark-green;
  padding-bottom: 1rem;
  color: $dark-green;
}
</style>
