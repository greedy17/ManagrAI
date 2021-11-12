<template>
  <div>
    <nav id="nav" v-if="userIsLoggedIn">
      <div class="logo">
        <img style="height: 3rem" src="@/assets/images/logo.png" />
      </div>

      <div class="left" ref="user-menu-icon">
        <div class="mar" v-if="isAdmin">
          <ul>
            <li>
              <router-link exact-active-class="active" :to="{ name: 'Integrations' }"
                >Connect
              </router-link>
            </li>
            <li>
              <router-link exact-active-class="active" :to="{ name: 'CustomizeLandingPage' }"
                >Map
              </router-link>
            </li>
            <li>
              <router-link active-class="active" :to="{ name: 'ListTemplates' }"
                >Workflows
              </router-link>
            </li>
            <li>
              <router-link exact-active-class="active" :to="{ name: 'InviteUsers' }"
                >Team</router-link
              >
            </li>
          </ul>
        </div>

        <div class="mar" v-else-if="!isAdmin && userLevel === 'MANAGER'">
          <ul>
            <li>
              <router-link
                v-if="isOnboarding"
                exact-active-class="active"
                :to="{ name: 'Integrations' }"
                >Onboarding
              </router-link>
              <router-link v-else exact-active-class="active" :to="{ name: 'Integrations' }"
                >Connect
              </router-link>
            </li>
            <li>
              <router-link
                v-if="!isOnboarding"
                active-class="active"
                :to="{ name: 'ListTemplates' }"
                >Workflows
              </router-link>
            </li>
            <li>
              <router-link
                v-if="!isOnboarding"
                exact-active-class="active"
                :to="{ name: 'InviteUsers' }"
                >Team</router-link
              >
            </li>
          </ul>
        </div>

        <div v-else class="mar">
          <ul>
            <li>
              <router-link
                v-if="isOnboarding"
                exact-active-class="active"
                :to="{ name: 'Integrations' }"
                >Onboarding
              </router-link>
              <router-link v-else exact-active-class="active" :to="{ name: 'Integrations' }"
                >Connect
              </router-link>
            </li>
            <li v-if="!isOnboarding">
              <router-link active-class="active" :to="{ name: 'ListTemplates' }"
                >Workflows
              </router-link>
            </li>
          </ul>
        </div>
      </div>

      <div v-if="!isAdmin && !user.onboarding" class="right">
        <div class="tooltip">
          <img style="height: 1.5rem" src="@/assets/images/blackhelp.png" class="tooltip__icon" />
          <div class="tooltip__popup">
            <div class="tooltip__popup__bold">Having issues?</div>
            <div class="tip">Email Us: support@mymanagr.com</div>
          </div>
        </div>

        <div>
          <router-link :to="{ name: 'ProfilePage' }"
            ><img src="@/assets/images/profile.png" style="height: 1.5rem" alt=""
          /></router-link>
        </div>

        <div>
          <router-link :to="{ name: 'Login' }"
            ><img
              @click="logOut"
              src="@/assets/images/blacklogout.png"
              alt=""
              style="height: 1.5rem"
          /></router-link>
        </div>
      </div>

      <div v-else-if="isAdmin" class="right">
        <div class="tooltip">
          <img style="height: 1.5rem" src="@/assets/images/blackhelp.png" class="tooltip__icon" />
          <div class="tooltip__popup">
            <div class="tooltip__popup__bold">Having issues?</div>
            <div class="tip">Email Us: support@mymanagr.com</div>
          </div>
        </div>

        <div>
          <router-link :to="{ name: 'ProfilePage' }"
            ><img src="@/assets/images/profile.png" style="height: 1.5rem" alt=""
          /></router-link>
        </div>

        <div>
          <router-link :to="{ name: 'Login' }"
            ><img
              @click="logOut"
              src="@/assets/images/blacklogout.png"
              alt=""
              style="height: 1.5rem"
          /></router-link>
        </div>
      </div>
    </nav>
  </div>
</template>

<script>
import DropDownMenu from '@/components/forms/DropDownMenu'
import { CollectionManager, Pagination } from '@thinknimble/tn-models'

import AlertTemplate, {
  AlertGroupForm,
  AlertTemplateForm,
  AlertConfigForm,
  AlertMessageTemplateForm,
  AlertOperandForm,
} from '@/services/alerts/'

export default {
  name: 'NavBar',
  components: {
    DropDownMenu,
    CollectionManager,
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
      userLevel: this.$store.state.user.userLevel,
      templates: CollectionManager.create({ ModelClass: AlertTemplate }),
    }
  },

  async created() {
    this.templates.refresh()
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
    hasSlack() {
      return this.$store.state.user.slackRef
    },
    hasSalesforce() {
      return this.$store.state.user.hasSalesforceIntegration
    },
    hasZoom() {
      return this.$store.state.user.hasZoomIntegration
    },
    hasNylas() {
      return this.$store.state.user.nylasRef
    },
    user() {
      return this.$store.state.user
    },
    isOnboarding() {
      return this.$store.state.user.onboarding
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
  position: fixed;
  top: 0;
  left: 0;
  z-index: 200;
  width: 100vw;
  background-color: #f2fff8;
  // box-shadow: 1px 4px 7px rgba(0, 0, 0, 0.2);
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
    height: 2rem;
  }

  &__popup {
    width: 18rem;
    visibility: hidden;

    padding: 13px 21px;
    border-radius: 5px;
    box-shadow: 0 5px 10px 0 rgba(0, 0, 0, 0.2);
    border: solid 2px $panther-gray;
    background-color: $panther;
    color: white;
    position: absolute;
    top: -5px;
    right: 105%;

    &__bold {
      font-family: #{$bold-font-family};
      color: $panther-silver;
    }
  }
}

.tooltip:hover .tooltip__popup {
  visibility: visible;
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
  border: 3px solid black;
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
  font-weight: bold;
  color: $black;
}

a:hover {
  filter: opacity(60%);
}
.mar {
  margin-top: 1rem;
}
.active {
  border-bottom: 3px solid $dark-green;
  font-weight: bold;
  padding-bottom: 0.5rem;
  color: black;
}
</style>