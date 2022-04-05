<template>
  <div>
    <nav id="nav" v-if="userIsLoggedIn">
      <div class="logo">
        <img style="height: 2rem" src="@/assets/images/logo.png" />
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
              <router-link exact-active-class="active" :to="{ name: 'Required' }"
                >Actions</router-link
              >
            </li>
            <li>
              <router-link active-class="active" :to="{ name: 'ListTemplates' }"
                >Workflows
              </router-link>
            </li>
            <li>
              <router-link exact-active-class="active" :to="{ name: 'Pipelines' }"
                >Pipeline</router-link
              >
            </li>
            <li>
              <router-link exact-active-class="active" :to="{ name: 'InviteUsers' }"
                >Team</router-link
              >
            </li>
            <li>
              <router-link exact-active-class="active" :to="{ name: 'Forecasting' }"
                >Forecast (coming soon)</router-link
              >
            </li>
            <li v-if="user.isStaff">
              <router-link exact-active-class="active" :to="{ name: 'Staff' }">Staff</router-link>
            </li>
          </ul>
        </div>

        <div class="mar" v-else-if="userLevel === 'MANAGER' && !isAdmin">
          <ul>
            <li>
              <router-link exact-active-class="active" :to="{ name: 'Integrations' }"
                >Connect
              </router-link>
            </li>
            <li>
              <router-link active-class="active" :to="{ name: 'ListTemplates' }"
                >Workflows
              </router-link>
            </li>
            <li>
              <router-link exact-active-class="active" :to="{ name: 'Pipelines' }"
                >Pipeline</router-link
              >
            </li>

            <li>
              <router-link exact-active-class="active" :to="{ name: 'InviteUsers' }"
                >Team</router-link
              >
            </li>
            <li>
              <router-link exact-active-class="active" :to="{ name: 'Forecasting' }"
                >Forecast (coming soon)</router-link
              >
            </li>
          </ul>
        </div>

        <div class="mar" v-else-if="userLevel === 'SDR'">
          <ul>
            <li>
              <router-link exact-active-class="active" :to="{ name: 'Integrations' }"
                >Connect
              </router-link>
            </li>
            <li>
              <router-link active-class="active" :to="{ name: 'ListTemplates' }"
                >Workflows
              </router-link>
            </li>
            <li>
              <router-link exact-active-class="active" :to="{ name: 'Pipelines' }"
                >Pipeline</router-link
              >
            </li>
            <li>
              <router-link exact-active-class="active" :to="{ name: 'Forecasting' }"
                >Forecast (coming soon)</router-link
              >
            </li>
          </ul>
        </div>

        <div v-else-if="userLevel === 'REP'">
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
            <li v-if="!isOnboarding">
              <router-link exact-active-class="active" :to="{ name: 'Pipelines' }"
                >Pipeline</router-link
              >
            </li>
            <li v-if="!isOnboarding">
              <router-link exact-active-class="active" :to="{ name: 'Forecasting' }"
                >Forecast (coming soon)</router-link
              >
            </li>
          </ul>
        </div>
      </div>

      <div v-if="userLevel == 'REP' && !user.onboarding" class="right">
        <div class="tooltip">
          <img
            style="height: 1.4rem; filter: invert(30%)"
            src="@/assets/images/blackhelp.png"
            class="tooltip__icon"
          />
          <div class="tooltip__popup">
            <div class="tooltip__popup__bold">Having issues?</div>
            <div class="tip">Email Us: support@mymanagr.com</div>
          </div>
        </div>

        <div>
          <router-link class="profile-wrapper" :to="{ name: 'ProfilePage' }">
            <img src="@/assets/images/profile.png" style="height: 1rem" alt="" />
          </router-link>
        </div>
        <div class="center">
          <router-link class="pad" :to="{ name: 'Login' }">
            <button class="logout">
              Log out
              <img
                @click="logOut"
                src="@/assets/images/blacklogout.png"
                alt=""
                style="height: 0.75rem; margin: 0.25rem"
              />
            </button>
          </router-link>
        </div>
      </div>

      <div v-if="userLevel !== 'REP'" class="right">
        <div class="tooltip">
          <img
            style="height: 1.4rem; filter: invert(30%)"
            src="@/assets/images/blackhelp.png"
            class="tooltip__icon"
          />
          <div class="tooltip__popup">
            <div class="tooltip__popup__bold">Having issues?</div>
            <div class="tip">Email Us: support@mymanagr.com</div>
          </div>
        </div>

        <div>
          <router-link class="profile-wrapper" :to="{ name: 'ProfilePage' }">
            <img src="@/assets/images/profile.png" style="height: 1rem" alt="" />
          </router-link>
        </div>
        <div class="center">
          <router-link class="pad" :to="{ name: 'Login' }">
            <button class="logout">
              Log out
              <img
                @click="logOut"
                src="@/assets/images/blacklogout.png"
                alt=""
                style="height: 0.75rem; margin: 0.25rem"
              />
            </button>
          </router-link>
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

span {
  font-size: 10px;
  color: $dark-green;
}
.profile-wrapper {
  border: none;
  background-color: $lighter-green;
  padding: 0.3rem 0.3rem 0.1rem 0.4rem;
  border-radius: 50%;
  img {
    filter: invert(50%) sepia(20%) saturate(1581%) hue-rotate(94deg) brightness(93%) contrast(90%);
  }
}
.profile-button {
  border: none;
  padding: 0.25rem;
  display: flex;
  justify-self: end;
  box-shadow: 1px 1px 2px $very-light-gray;
  border-radius: 0.5rem;
  background-color: $soft-gray;
  cursor: pointer;
  color: $base-gray;
  font-weight: bold;
}
.center {
  display: flex;
  align-items: center;
  justify-content: center;
}
.logout {
  border: none;
  padding: 0.25rem 0.5rem;
  margin-top: 0.75rem;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  box-shadow: 1px 1px 2px $very-light-gray;
  border-radius: 0.5rem;
  background-color: $soft-gray;
  cursor: pointer;
  color: $base-gray;
  font-weight: bold;
}
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
  color: $base-gray;
  padding: 0.25rem 0 1rem 0;
  border-bottom: 3px solid $soft-gray;
  -webkit-backdrop-filter: blur(8px);
  backdrop-filter: blur(8px);
}
.logo {
  margin-left: 1.5rem;
  margin-right: 2.25rem;
  display: flex;
  flex-direction: row;
  align-items: flex-end;
  justify-content: center;
  cursor: pointer;
  font-weight: 400;
  font-size: 1.5rem;
  padding: 0.75rem;
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
  margin-top: 0.75rem;

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
    padding: 0.5rem;
    min-width: 14vw;
    visibility: hidden;
    border-radius: 5px;
    box-shadow: 0 5px 10px 0 rgba(0, 0, 0, 0.2);
    border: solid 2px $off-white;
    background-color: $off-white;
    color: $base-gray;
    position: absolute;
    top: -5px;
    right: 105%;

    &__bold {
      font-family: #{$bold-font-family};
      color: $panther;
      font-size: 14px;
    }
  }
}
.tip {
  font-size: 11px;
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
  letter-spacing: 0.4px;
  text-align: center;
  margin-right: 1rem;
  font-size: 13px;
  padding: 0.5rem;
  @media only screen and (max-width: 800px) {
    margin-right: 0.5rem;
    font-size: 11px;
  }
  @media only screen and (max-width: 700px) {
    margin-right: 0.25rem;
    font-size: 10px;
  }
}

@media only screen and (max-width: 768px) {
  img {
    height: 0.5rem;
  }
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
  color: $base-gray;
  font-family: #{$base-font-family};
  font-weight: bold;
}

li:hover {
  background-color: $lighter-green;
  border-radius: 0.2rem;
  color: white;
}
.mar {
  margin-top: 1rem;
}
.active {
  border-bottom: 3px solid $dark-green;
  color: $dark-green;
  padding-bottom: 1rem;
}
</style>
