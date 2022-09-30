<template>
  <div>
    <nav id="nav" v-if="userIsLoggedIn">
      <router-link :to="{ name: 'Pipelines' }">
        <div class="logo">
          <img style="height: 40px" src="@/assets/images/logo.png" />
        </div>
      </router-link>

      <div style="height: 100%" class="align-left">
        <!-- <router-link active-class="active" :to="{ name: 'Home' }">
          <div class="tooltip">
            <img src="@/assets/images/star.svg" height="16px" alt="" />
            <span class="tooltiptext">Home</span>
          </div>
        </router-link> -->
        <router-link active-class="active" :to="{ name: 'ListTemplates' }">
          <div class="tooltip">
            <img src="@/assets/images/workflows.svg" height="16px" alt="" />
            <span class="tooltiptext">Workflows</span>
          </div>
        </router-link>

        <router-link exact-active-class="active" :to="{ name: 'Pipelines' }">
          <div class="tooltip">
            <img src="@/assets/images/pipeline.svg" height="16px" alt="" />
            <span class="tooltiptext">Pipeline</span>
          </div>
        </router-link>

        <!-- <router-link exact-active-class="active" :to="{ name: 'Meetings' }">
          <div class="tooltip">
            <img src="@/assets/images/calendar.svg" height="16px" alt="" />
            <span class="tooltiptext">Meetings</span>
          </div>
        </router-link> -->

        <router-link
          v-if="isTeamLead || isAdmin"
          exact-active-class="active"
          :to="{ name: 'UpdateOpportunity' }"
        >
          <div class="tooltip">
            <img src="@/assets/images/list.svg" height="16px" alt="" />
            <span class="tooltiptext">Forms</span>
          </div>
        </router-link>

        <!-- <router-link exact-active-class="active" :to="{ name: 'Forecast' }">
          <div class="tooltip">
            <img src="@/assets/images/tracker.svg" height="16px" alt="" />
            <span class="tooltiptext">Tracker</span>
          </div>
         
        </router-link> -->

        <li v-if="user.isStaff">
          <router-link exact-active-class="active" :to="{ name: 'Staff' }">Admin</router-link>
        </li>

        <router-link exact-active-class="active" :to="{ name: 'Integrations' }">
          <div class="tooltip">
            <img src="@/assets/images/connect.svg" class="nav-img" height="16px" alt="" />
            <span class="tooltiptext">Integrations</span>
          </div>
        </router-link>

        <!-- <router-link
          v-if="isTeamLead || isAdmin"
          exact-active-class="active-img"
          :to="{ name: 'Required' }"
        >
          <div class="tooltip">
            <img src="@/assets/images/list.svg" height="16px" alt="" />
            <span class="tooltiptext">Forms</span>
          </div>
        </router-link> -->

        <!-- <router-link active-class="active" :to="{ name: 'ListTemplates' }">
          <div class="tooltip">
            <img src="@/assets/images/workflows.svg" height="16px" alt="" />
            <span class="tooltiptext">Workflows</span>
          </div>
        </router-link> -->

        <!-- @click="goToProfile(Math.floor(Math.random() * 10000))" -->
        <router-link
          exact-active-class="active"
          v-if="routeName === 'InviteUsers'"
          :to="{ name: 'InviteUsers' }"
        >
          <div class="tooltip">
            <img src="@/assets/images/profile.svg" height="16px" alt="" />
            <span class="tooltiptext">Profile</span>
          </div>
        </router-link>

        <router-link exact-active-class="active" v-else :to="{ name: 'InviteUsers' }">
          <div class="tooltip">
            <img src="@/assets/images/profile.svg" height="16px" alt="" />
            <span class="tooltiptext">Profile</span>
          </div>
        </router-link>

        <!-- <router-link exact-active-class="active" :to="{ name: 'Meetings' }">
          <div class="tooltip">
            <img src="@/assets/images/calendar.svg" height="16px" alt="" />
            <span class="tooltiptext">Meetings</span>
          </div>
        </router-link> -->

        <router-link style="margin-top: auto" :to="{ name: 'Login' }">
          <div>
            <img @click="logOut" src="@/assets/images/logout.svg" alt="" height="16px" />
          </div>
        </router-link>
      </div>

      <!-- <div v-else class="right">
        <router-link exact-active-class="active-img" :to="{ name: 'Integrations' }">
          <div class="tooltip">
            <img src="@/assets/images/connect.svg" class="nav-img" alt="" />
            <span class="tooltiptext">Integrations</span>
          </div>
        </router-link>

        <router-link
          v-if="isTeamLead || this.isAdmin"
          exact-active-class="active-img"
          :to="{ name: 'Required' }"
        >
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
    if (this.isTeamLead || this.isAdmin) {
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
    isTeamLead() {
      return this.userIsLoggedIn && this.$store.state.user.isTeamLead
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
    opacity: 0.9;
    transform: translate(10%, 0%);
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
  width: 72px;
  background-color: white;
  padding: 0px 4px;
  border-right: 1px solid $soft-gray;
}
.logo {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: flex-start;
  margin-top: -8px;
  margin-left: -4px;
  margin-bottom: 12px;
  cursor: pointer;
  filter: brightness(0%) saturate(100%) invert(63%) sepia(31%) saturate(743%) hue-rotate(101deg)
    brightness(93%) contrast(89%);
}
.align-left {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: flex-start;
  margin-bottom: 16px;
  padding: 0;
  margin-left: -8px;
  // > * {
  //   margin-right: 1rem;
  // }
}

img {
  margin-top: 1rem;
}
a {
  text-decoration: none;
  color: $base-gray;
  font-family: #{$base-font-family};
  font-weight: bold;
  padding: 16px 12px;
  img {
    transition: all 0.2s;
  }
}
a:hover {
  color: white;
}

.mar {
  margin-top: 1rem;
}
.active {
  // img {
  //   filter: invert(99%);
  // }
  background-color: $white-green;
  margin: 14px 0px 4px 0px;
  padding-top: 0px;
  border-radius: 4px;
  img {
    filter: brightness(0%) saturate(100%) invert(63%) sepia(31%) saturate(743%) hue-rotate(101deg)
      brightness(93%) contrast(89%);
  }
}

.tooltip {
  position: relative;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 4px 0px;
}
.tooltip .tooltiptext {
  visibility: hidden;
  width: 160px;
  background-color: $base-gray;
  color: white;
  text-align: center;
  border: none !important;
  letter-spacing: 1px;
  padding: 8px 0;
  border-radius: 6px;
  font-size: 12px;
  font-weight: bold !important;
  position: absolute;
  z-index: 1;
  top: 4px;
  left: 270%;
  margin-left: -32px;
  opacity: 70%;
  transition: opacity 0.3s;
}

.tooltip:hover .tooltiptext {
  visibility: visible;
  animation: tooltips-horz 300ms ease-out forwards;
}
.end {
  height: 20vh;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
}
// @media screen and (max-width: 700px) {
//   nav {
//     width: 100%;
//     display: flex;
//     flex-direction: row;
//   }
//   nav a {
//     float: left;
//   }
//   div.content {
//     margin-left: 0;
//   }
// }

// @media screen and (max-width: 400px) {
//   nav a {
//     text-align: center;
//     float: none;
//   }
// }
</style>
