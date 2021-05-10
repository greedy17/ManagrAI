<template>
  <div>
    <nav id="nav">
      <div class="logo">
        <img src="@/assets/images/logo-with-name.png" />
      </div>

      <div class="right" ref="user-menu-icon">
        <div>
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
        </div>

        <div v-if="userIsLoggedIn" class="right__items" @click="toggleDropDown">
          <DropDownMenu
            @selectedItem="routeToSelected"
            :right="10"
            :items="[
              { key: 'Integrations', value: 'Integrations' },
              { key: 'Slack Forms', value: 'SlackFormSettings' },
              { key: 'Invite Users', value: 'InviteUsers' },
              { key: 'Notifications and Alerts', value: 'CreateNew' },
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
              { key: 'Notifications and Alerts', value: 'CreateNew' },

              { key: 'Log Out', value: 'logout' },
            ]"
            v-if="!isAdmin"
          >
            <template v-slot:dropdown-trigger="{ toggle }">
              <svg ref="dd-user-settings" @click="toggle" class="dd-icon" viewBox="-5 0 24 18">
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

.tooltip {
  position: relative;
  &__icon {
    width: 18px;
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
</style>
