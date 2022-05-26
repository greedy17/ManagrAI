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
              <router-link exact-active-class="active" :to="{ name: 'Meetings' }"
                >Meetings</router-link
              >
            </li>
            <li>
              <router-link exact-active-class="active" :to="{ name: 'InviteUsers' }"
                >Team</router-link
              >
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
              <router-link exact-active-class="active" :to="{ name: 'Meetings' }"
                >Meetings</router-link
              >
            </li>
            <li>
              <router-link exact-active-class="active" :to="{ name: 'InviteUsers' }"
                >Team</router-link
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
              <router-link exact-active-class="active" :to="{ name: 'Meetings' }"
                >Meetings</router-link
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
              <router-link exact-active-class="active" :to="{ name: 'Meetings' }"
                >Meetings</router-link
              >
            </li>
          </ul>
        </div>
      </div>

      <div v-if="userLevel == 'REP' && !user.onboarding" class="right">
        <div class="tooltip">
          <img
            style="height: 1.2rem; filter: invert(30%)"
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
            <small>{{ user.email }}</small>
            <img src="@/assets/images/profile.png" alt="" />
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
            style="height: 1.2rem; filter: invert(30%)"
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
            <small>{{ user.email }}</small>
            <img src="@/assets/images/profile.png" alt="" />
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
import { CollectionManager } from '@thinknimble/tn-models'

import AlertTemplate from '@/services/alerts/'

export default {
  name: 'NavBar',
  components: {
    CollectionManager,
  },
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
    logOut() {
      this.$store.dispatch('logoutUser')
      this.$router.push({ name: 'Login' })
    },
  },
  computed: {
    userIsLoggedIn() {
      return this.$store.getters.userIsLoggedIn
    },
    isAdmin() {
      return this.userIsLoggedIn && this.$store.state.user.isAdmin
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

.nameOrg {
  display: flex;
  flex-direction: row;
  align-items: center;
  p {
    font-size: 11px;
  }
  small {
    font-size: 10px;
    margin-left: 0.2rem;
    color: $dark-green;
  }
}
span {
  font-size: 10px;
  color: $dark-green;
}
.profile-wrapper {
  display: flex !important;
  align-items: center !important;
  border: none;
  margin: 1rem 0rem 0.25rem 0rem;
  background-color: $soft-gray;
  padding: 0.2rem;
  border-radius: 0.3rem;
  small {
    font-size: 10px;
    margin-right: 0.5rem;
    margin-left: 0.25rem;
    color: $base-gray;
    letter-spacing: 0.25px;
  }
  img {
    filter: invert(63%) sepia(31%) saturate(743%) hue-rotate(101deg) brightness(93%) contrast(89%);
    margin-top: 0.2rem;
    height: 1.2rem;
  }
}
.center {
  display: flex;
  align-items: center;
  justify-content: center;
}
.logout {
  border: 1px solid #e8e8e8;
  padding: 0.25rem 0.5rem;
  margin-top: 0.75rem;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  border-radius: 0.3rem;
  background-color: $soft-gray;
  cursor: pointer;
  color: $base-gray;
  font-size: 11px;
}
nav {
  height: 3.5rem;
  display: flex;
  flex-flow: row;
  align-items: center;
  position: fixed;
  top: 0;
  left: 0;
  z-index: 200;
  width: 100vw;
  padding: 0.25rem 0 1rem 0;
  border-bottom: 2px solid $soft-gray;
  -webkit-backdrop-filter: blur(8px);
  backdrop-filter: blur(8px);
}
.logo {
  margin-left: 0.5rem;
  margin-right: 1rem;
  display: flex;
  flex-direction: row;
  align-items: flex-end;
  justify-content: center;
  cursor: pointer;
  padding: 0.5rem;
  filter: brightness(0%) saturate(100%) invert(63%) sepia(31%) saturate(743%) hue-rotate(101deg)
    brightness(93%) contrast(89%);
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
}
.left {
  margin-right: auto;
  display: flex;
  flex-direction: row;
  justify-content: space-evenly;
  position: relative;
  margin-right: 0.75rem;
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
      color: $base-gray;
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
ul:hover {
  color: white;
}

li {
  display: inline;
  letter-spacing: 0.4px;
  text-align: center;
  margin-right: 0.75rem;
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

img {
  margin-top: 1rem;
}
a {
  text-decoration: none;
  color: $base-gray;
  font-family: #{$base-font-family};
  font-weight: bold;
  padding: 0.5rem 0.2rem;
}
a:hover {
  color: white;
}

li:hover {
  background-color: $dark-green;
  border-radius: 0.2rem;
  color: white;
}
.mar {
  margin-top: 1rem;
}
.active {
  border-bottom: 2.25px solid $dark-green;
  color: $dark-green;
  padding-bottom: 0.9rem;
}
</style>
