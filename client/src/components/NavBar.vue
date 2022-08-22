<template>
  <div>
    <nav id="nav" v-if="userIsLoggedIn">
      <router-link :to="{ name: 'Pipelines' }">
        <div class="logo">
          <img style="height: 40px" src="@/assets/images/logo.png" />
        </div>
      </router-link>

      <ul class="align-left">
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
          <router-link exact-active-class="active" :to="{ name: 'Meetings' }">Meetings</router-link>
        </li>
        <li>
          <router-link exact-active-class="active" :to="{ name: 'Forecast' }"
            >Tracker <span>Beta</span>
          </router-link>
        </li>
        <li v-if="user.isStaff">
          <router-link exact-active-class="active" :to="{ name: 'Staff' }">Admin</router-link>
        </li>
      </ul>

      <!-- <div class="mar">
          <ul>
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
            <li v-if="!isOnboarding">
              <router-link exact-active-class="active" :to="{ name: 'Forecast' }"
                >Tracker<span>Beta</span></router-link
              >
            </li>
          </ul>
        </div> -->

      <div class="right">
        <router-link exact-active-class="active-img" :to="{ name: 'Integrations' }">
          <div class="tooltip">
            <img src="@/assets/images/connect.svg" class="nav-img" alt="" />
            <span class="tooltiptext">Integrations</span>
          </div>
        </router-link>

        <router-link v-if="isAdmin" exact-active-class="active-img" :to="{ name: 'Required' }">
          <div class="tooltip">
            <img src="@/assets/images/list.svg" alt="" />
            <span class="tooltiptext">Forms</span>
          </div>
        </router-link>

        <div v-if="routeName === 'InviteUsers'">
          <div style="cursor: pointer" @click="goToProfile(Math.floor(Math.random() * 10000))">
            <div class="tooltip">
              <img src="@/assets/images/profile.svg" alt="" />
              <span class="tooltiptext">Profile</span>
            </div>
          </div>
        </div>

        <div v-else>
          <router-link :to="{ name: 'InviteUsers' }">
            <div class="tooltip">
              <img src="@/assets/images/profile.svg" height="16px" alt="" />
              <span class="tooltiptext">Profile</span>
            </div>
          </router-link>
        </div>

        <div>
          <router-link :to="{ name: 'Login' }">
            <img @click="logOut" src="@/assets/images/logout.svg" alt="" height="16px" />
          </router-link>
        </div>
      </div>

      <!-- <div v-else class="right">
        <router-link exact-active-class="active-img" :to="{ name: 'Integrations' }">
          <div class="tooltip">
            <img src="@/assets/images/connect.svg" class="nav-img" alt="" />
            <span class="tooltiptext">Integrations</span>
          </div>
        </router-link>

        <router-link v-if="isAdmin" exact-active-class="active-img" :to="{ name: 'Required' }">
          <div class="tooltip">
            <img src="@/assets/images/list.svg" alt="" />
            <span class="tooltiptext">Forms</span>
          </div>
        </router-link>

        <div v-if="routeName === 'InviteUsers'">
          <div style="cursor: pointer" @click="goToProfile(Math.floor(Math.random() * 10000))">
            <div class="tooltip">
              <small class="profile-wrapper">{{ user.email }}</small>
              <span class="tooltiptext">Profile</span>
            </div>
          </div>
        </div>

        <div v-else>
          <router-link :to="{ name: 'InviteUsers' }">
            <div class="tooltip">
              <small class="profile-wrapper">{{ user.email }}</small>
            
              <span class="tooltiptext">Profile</span>
            </div>
          </router-link>
        </div>

        <div class="center">
          <router-link :to="{ name: 'Login' }">
            <img @click="logOut" src="@/assets/images/logout.svg" alt="" height="16px" />
          </router-link>
        </div>
      </div> -->
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
      localStorage.isLoggedOut = true
    },
    goToProfile(id) {
      this.$router.push({ path: `/invite-users/${id}` })
    },
  },
  computed: {
    userIsLoggedIn() {
      return this.$store.getters.userIsLoggedIn
    },
    routeName() {
      return this.$route.name
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

@media only screen and (max-width: 600px) {
}
/* Small devices (portrait tablets and large phones, 600px and up) */
@media only screen and (min-width: 600px) {
}
/* Medium devices (landscape tablets, 768px and up) */
@media only screen and (min-width: 768px) {
}
/* Large devices (laptops/desktops, 992px and up) */
@media only screen and (min-width: 992px) {
}
/* Extra large devices (large laptops and desktops, 1200px and up) */
@media only screen and (min-width: 1200px) {
}
@keyframes tooltips-horz {
  to {
    opacity: 0.95;
    transform: translate(0%, 50%);
  }
}

.nav-img {
  height: 16px;
}

span {
  font-size: 11px;
  color: $dark-green;
  background-color: #f3f0f0;
  margin-left: 0.25rem;
  padding: 0.2rem;
  border-radius: 0.2rem;
}
.profile-wrapper {
  font-size: 10px;
  color: $base-gray;
  letter-spacing: 0.25px;
  border: none;
  margin: 1.2rem 0rem 0.25rem 0rem;
  background-color: #f3f0f0;
  padding: 4px 6px;
  border-radius: 6px;
  // small {
  //   font-size: 10px;
  //   margin-right: 0.5rem;
  //   margin-left: 0.25rem;
  //   color: $base-gray;
  //   letter-spacing: 0.25px;
  // }
  // img {
  //   filter: invert(63%) sepia(31%) saturate(743%) hue-rotate(101deg) brightness(93%) contrast(89%);
  //   margin-top: 0.2rem;
  //   height: 1.2rem;
  // }
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
  height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: fixed;
  top: 0;
  left: 0;
  z-index: 20;
  width: 120px;
  background-color: white;
  padding: 8px 0px;
  border-right: 1px solid $soft-gray;
}
.logo {
  display: flex;
  align-items: flex-start;
  justify-content: center;
  margin-bottom: 32px;
  cursor: pointer;
  filter: brightness(0%) saturate(100%) invert(63%) sepia(31%) saturate(743%) hue-rotate(101deg)
    brightness(93%) contrast(89%);
}
.right {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  margin-bottom: 16px;
  margin-left: 8px;
  // > * {
  //   margin-right: 1rem;
  // }
}

ul {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  list-style-type: none;
  margin: 0;
  margin-left: -7px;
  padding: 0;
}
ul:hover {
  color: white;
}

li {
  display: inline;
  letter-spacing: 0.4px;
  text-align: center;
  margin-bottom: 12px;
  font-size: 12px;
  padding: 8px;
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
.active-img {
  border-bottom: 2.25px solid $dark-green;
  color: $dark-green;
}
.active {
  border-bottom: 2.25px solid $dark-green;
  color: $dark-green;
  padding-bottom: 0.9rem;

  img {
    filter: brightness(0%) saturate(100%) invert(63%) sepia(31%) saturate(743%) hue-rotate(101deg)
      brightness(93%) contrast(89%);
  }
}

.tooltip {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 2px 0px;
}
.tooltip .tooltiptext {
  visibility: hidden;
  background-color: $base-gray;
  color: white;
  text-align: center;
  border: 1px solid $soft-gray;
  letter-spacing: 0.5px;
  padding: 4px 0px;
  border-radius: 6px;
  font-size: 12px;

  /* Position the tooltip text */
  position: absolute;
  z-index: 1;
  width: 100px;
  top: 100%;
  left: 50%;
  margin-left: -50px;

  /* Fade in tooltip */
  opacity: 0;
  transition: opacity 0.3s;
}
.tooltip:hover .tooltiptext {
  visibility: visible;
  animation: tooltips-horz 300ms ease-out forwards;
}
</style>
