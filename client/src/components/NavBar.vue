<template>
  <div>
    <nav id="nav" v-if="userIsLoggedIn">
      <router-link v-if="userCRM" :to="{ name: 'ListTemplates' }">
        <div class="logo">
          <img style="height: 40px" src="@/assets/images/logo.png" />
        </div>
      </router-link>

      <router-link v-else :to="{ name: 'Integrations' }">
        <div class="logo">
          <img style="height: 40px" src="@/assets/images/logo.png" />
        </div>
      </router-link>

      <div v-if="!isOnboarding" style="height: 100%" class="align-left">
        <router-link v-if="userCRM" class="side-wrapper" active-class="active" :to="{ name: 'ListTemplates' }">
          <label class="side-icon side-workflow" style="margin: 8px 0 0 0;">
            <span class="side-tooltip-single" style="top: -5px; width: 80px;">Workflows</span>
            <img src="@/assets/images/workflows.svg" class="nav-img" height="16px" alt="" style="margin-top: 0;" />
          </label>
        </router-link>

        <router-link v-if="userCRM" class="side-wrapper" exact-active-class="active" :to="{ name: 'Pipelines' }">
          <label class="side-icon side-workflow" style="margin: 8px 0 0 0;">
            <span class="side-tooltip-single" style="top: -5px; width: 65px;">Pipeline</span>
            <img src="@/assets/images/pipeline.svg" class="nav-img" height="16px" alt="" style="margin-top: 0;" />
          </label>
        </router-link>

        <router-link
          v-if="(isTeamLead || isAdmin) && userCRM"
          class="side-wrapper"
          exact-active-class="active"
          :to="{ name: 'Forms' }"
        >
          <label class="side-icon side-workflow" style="margin: 8px 0 0 0;">
            <span class="side-tooltip-single" style="top: -5px; width: 55px;">Forms</span>
            <img src="@/assets/images/edit-note.svg" class="nav-img" height="16px" alt="" style="margin-top: 0;" />
          </label>
        </router-link>

        <router-link
          v-if="userCRM === 'SALESFORCE'"
          class="side-wrapper"
          exact-active-class="active"
          :to="{ name: 'Meetings' }"
        >
          <label class="side-icon side-workflow" style="margin: 8px 0 0 0;">
            <span class="side-tooltip-single" style="top: -5px; width: 75px;">Meetings</span>
            <img src="@/assets/images/calendar.svg" class="nav-img" height="16px" alt="" style="margin-top: 0;" />
          </label>
        </router-link>

        <router-link v-if="userCRM" class="side-wrapper" exact-active-class="active" :to="{ name: 'Notes' }">
          <label class="side-icon side-workflow" style="margin: 8px 0 0 0;">
            <span class="side-tooltip-single" style="top: -5px; width: 120px;">Note Templates</span>
            <img src="@/assets/images/notebook.svg" class="nav-img" height="16px" alt="" style="margin-top: 0;" />
          </label>
        </router-link>

        <router-link class="side-wrapper" exact-active-class="active" :to="{ name: 'Integrations' }">
          <label class="side-icon side-workflow" style="margin: 8px 0 0 0;">
            <span class="side-tooltip-single" style="top: -5px;">Integrations</span>
            <img src="@/assets/images/connect.svg" class="nav-img" height="16px" alt="" style="margin-top: 0;" />
          </label>
        </router-link>
        <router-link
          class="side-wrapper"
          exact-active-class="active"
          v-if="routeName === 'InviteUsers' && userCRM"
          :to="{ name: 'InviteUsers' }"
        >
          <label class="side-icon side-workflow" style="margin: 8px 0 0 0;">
            <span class="side-tooltip-single" style="top: -5px; width: 60px;">Profile</span>
            <img src="@/assets/images/profile.svg" class="nav-img" height="16px" alt="" style="margin-top: 0;" />
          </label>
        </router-link>

        <router-link class="side-wrapper" exact-active-class="active" v-else-if="userCRM" :to="{ name: 'InviteUsers' }">
          <label class="side-icon side-workflow" style="margin: 8px 0 0 0;">
            <span class="side-tooltip-single" style="top: -5px; width: 60px;">Profile</span>
            <img src="@/assets/images/profile.svg" class="nav-img" height="16px" alt="" style="margin-top: 0;" />
          </label>
        </router-link>

        <router-link v-if="!isPaid" class="side-wrapper" exact-active-class="active" :to="{ name: 'Reports' }">
          <label class="side-icon side-workflow" style="margin: 8px 0 0 0;">
            <span class="side-tooltip-single" style="top: -5px; width: 190px;">Reports: Upgrade your plan</span>
            <img src="@/assets/images/reports.svg" class="nav-img" height="16px" alt="" style="margin-top: 0;" />
          </label>
        </router-link>
        <router-link v-else class="side-wrapper" exact-active-class="active" :to="{ name: 'Reports' }">
          <label class="side-icon side-workflow" style="margin: 8px 0 0 0;">
            <span class="side-tooltip-single" style="top: -5px; width: 60px;">Reports</span>
            <img src="@/assets/images/reports.svg" class="" height="16px" alt="" style="margin-top: 0;" />
          </label>
        </router-link>

        <div class="side-wrapper" style="margin-top: auto">
          <label class="side-icon side-workflow" style="">
            <span class="side-tooltip"><div>Need help?</div><div>Email: cx@mymanagr.com</div></span>
            <img
              src="@/assets/images/help.png"
              class="side-img"
              style="margin-top: 0"
              height="16px"
              alt=""
            />
          </label>
        </div>

        <router-link :to="{ name: 'Login' }">
          <div style="margin-left: 3px">
            <img @click="logOut" src="@/assets/images/logout.svg" alt="" height="16px" />
          </div>
        </router-link>
      </div>
      <div v-else style="height: 100%" class="align-left">
        <router-link v-if="userCRM" active-class="active" :to="{ name: 'ListTemplates' }">
          <div class="tooltip">
            <img src="@/assets/images/handshake.svg" height="18px" alt="" />
            <span class="tooltiptext">Onboarding</span>
          </div>
        </router-link>
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
      items: [],
    }
  },

  async created() {
    if (this.isTeamLead || this.isAdmin) {
      this.items = [
        { key: 'Integrations', value: 'Integrations' },
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
  },
  computed: {
    isOnboarding() {
      return this.$store.state.user.onboarding
    },
    isPaid() {
      return !!this.$store.state.user.organizationRef.isPaid
    },
    userIsLoggedIn() {
      return this.$store.getters.userIsLoggedIn
    },
    userCRM() {
      return this.$store.state.user.crm
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
nav {
  height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: fixed;
  top: 0;
  left: 0;
  z-index: 20;
  width: 60px;
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
  // padding: 16px 12px;
  padding: 12px 12px 10px 12px;
  img {
    transition: all 0.2s;
  }
}
a:hover {
  color: white;
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

.tooltip-wide {
  position: relative;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 4px 0px;
}
.tooltip-wide .tooltiptext-wide {
  visibility: hidden;
  width: 240px;
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

.tooltip-wide:hover .tooltiptext-wide {
  visibility: visible;
  animation: tooltips-horz 300ms ease-out forwards;
}

// Tooltip
.side-wrapper {
  display: flex;
  flex-direction: row;
}
.side-wrapper .side-icon {
  position: relative;
  // background: #FFFFFF;
  border-radius: 50%;
  padding: 12px;
  margin: 20px 12px 0px 10px;
  width: 18px;
  height: 18px;
  font-size: 13px;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  // outline: 1px solid $mid-gray;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}
.side-wrapper .side-tooltip,
.side-wrapper .side-tooltip-single {
  display: block;
  width: 250px;
  height: auto;
  position: absolute;
  top: -10px; // for double line
  // top: 0; // for single line
  left: 30px;
  font-size: 14px;
  background: #ffffff;
  color: #ffffff;
  padding: 6px 8px;
  border-radius: 5px;
  box-shadow: 0 10px 10px rgba(0, 0, 0, 0.1);
  opacity: 0;
  pointer-events: none;
  line-height: 1.5;
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}
.side-wrapper .side-tooltip-single {
  width: 100px;
}
.side-wrapper .side-tooltip::before,
.side-wrapper .side-tooltip-single::before {
  position: absolute;
  content: '';
  height: 8px;
  width: 8px;
  background: #ffffff;
  bottom: 50%;
  left: 0%;
  transform: translate(-50%) rotate(45deg);
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}
.side-wrapper .side-tooltip-single::before {
  bottom: 40%;
}
.side-wrapper .side-icon:hover .side-tooltip,
.side-wrapper .side-icon:hover .side-tooltip-single {
  opacity: 1;
  visibility: visible;
  pointer-events: auto;
}
.side-wrapper .side-icon:hover span,
.side-wrapper .side-icon:hover .side-tooltip,
.side-wrapper .side-icon:hover .side-tooltip-single {
  text-shadow: 0px -1px 0px rgba(0, 0, 0, 0.1);
}
.side-wrapper .side-workflow:hover,
.side-wrapper .side-workflow:hover .side-tooltip,
.side-wrapper .side-workflow:hover .side-tooltip::before,
.side-wrapper .side-workflow:hover .side-tooltip-single,
.side-wrapper .side-workflow:hover .side-tooltip-single::before {
  // margin-top: 1rem;
  background: $grape;
  color: #ffffff;
}
.side-icon:hover {
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
  img {
    filter: invert(90%);
  }
}
// .side-img:hover {
//   filter: invert(90%);
// }
</style>
