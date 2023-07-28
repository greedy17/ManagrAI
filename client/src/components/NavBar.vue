<template>
  <div>
    <Modal v-if="modalOpen" @close-modal="closeModal" dimmed>
      <div class="command-modal">
        <header>
          <div>
            <h2>
              How to use chatbot 💬
              <img
                src="@/assets/images/slackLogo.png"
                style="margin-left: 6px"
                height="18px"
                alt=""
              />
            </h2>
            <p>Use conversational AI to update CRM and take actions.</p>
          </div>

          <img
            @click="closeModal()"
            src="@/assets/images/close.svg"
            style="filter: invert(40%)"
            height="24px"
            alt=""
          />
        </header>
        <section>
          <div>
            <h5><span>1. Run a command in Slack</span></h5>
            <p>Type '/' into any Slack message box to initiate a command</p>
          </div>
          <div>
            <h5><span>2. Select 1 of 2 chatbot commands</span></h5>
            <p>
              Search for "Managr-update" to update the CRM. Use "Managr-actions" to get real-time
              insights
            </p>
          </div>
          <div style="border-bottom: none; padding-top: 1rem">
            <h5>
              🤖 ☁️
              <span>{{
                `Using Managr-update: make sure to include ${
                  userCRM === 'SALESFORCE' ? 'Opportunity + Opportunity Name.' : 'Deal + Deal Name.'
                }`
              }}</span>
            </h5>
            <p style="padding-left: 2.4rem">
              Ex: Push close date for Opportunity Pied Piper 2 weeks.
            </p>
          </div>
          <div style="border-bottom: none; padding-top: 1rem">
            <h5>
              🤖 🦾
              <span>Using Managr-actions: select from the dropdown.</span>
            </h5>
            <p style="padding-left: 2.4rem">
              Get a deal summary, run a deal review, or schedule a meeting (coming soon!)
            </p>
          </div>
          <!-- <div>
            <img
              style="border: 1px solid #eeeeee; border-radius: 8px"
              src="@/assets/images/chatbot.png"
              height="300px"
              alt=""
            />
          </div> -->
        </section>
      </div>
    </Modal>

    <div v-if="userIsLoggedIn">
      <nav id="nav" v-if="isPR">
        <router-link :to="{ name: 'PRSummaries' }">
          <div class="logo">
            <img style="height: 40px" src="@/assets/images/logo.png" />
          </div>
        </router-link>

        <div style="height: 100%" class="align-left">
          <router-link class="side-wrapper" active-class="active" :to="{ name: 'PRSummaries' }">
            <label class="side-icon side-workflow" style="margin: 8px 0 0 0">
              <span class="side-tooltip-single" style="top: -5px; width: 80px">Summaries</span>
              <img
                src="@/assets/images/search-alt.svg"
                class="nav-img"
                height="16px"
                alt=""
                style="margin-top: 0"
              />
            </label>
          </router-link>
          <router-link class="side-wrapper" active-class="active" :to="{ name: 'PRClipReport' }">
            <label class="side-icon side-workflow" style="margin: 8px 0 0 0">
              <span class="side-tooltip-single" style="top: -5px; width: 80px">Clip Report</span>
              <img
                src="@/assets/images/file-excel.svg"
                class="nav-img"
                height="16px"
                alt=""
                style="margin-top: 0"
              />
            </label>
          </router-link>
          <div
            class="side-wrapper margin-customize"
            active-class="active"
            @click="test('Customize')"
          >
            <label class="side-icon side-workflow" style="margin: 8px 0 0 0">
              <span class="side-tooltip-single" style="top: -5px; width: 80px">Customize</span>
              <img
                src="@/assets/images/magic-wand.svg"
                class="nav-img"
                height="16px"
                alt=""
                style="margin-top: 0"
              />
            </label>
          </div>
        </div>
        <router-link :to="{ name: 'Login' }" style="margin-top: auto">
          <div style="margin-left: 5px">
            <img @click="logOut" src="@/assets/images/logout.svg" alt="" height="16px" />
          </div>
        </router-link>
      </nav>
      <!-- <nav id="nav" v-else>
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
  
        <div v-if="!isOnboarding || !isAdmin" style="height: 100%" class="align-left">
          <router-link
            v-if="userCRM"
            class="side-wrapper"
            active-class="active"
            :to="{ name: 'ListTemplates' }"
          >
            <label class="side-icon side-workflow" style="margin: 8px 0 0 0">
              <span class="side-tooltip-single" style="top: -5px; width: 80px">Workflows</span>
              <img
                src="@/assets/images/workflows.svg"
                class="nav-img"
                height="16px"
                alt=""
                style="margin-top: 0"
              />
            </label>
          </router-link>
  
          <router-link
            v-if="userCRM"
            class="side-wrapper"
            exact-active-class="active"
            :to="{ name: 'Pipelines' }"
          >
            <label class="side-icon side-workflow" style="margin: 8px 0 0 0">
              <span class="side-tooltip-single" style="top: -5px; width: 65px">Pipeline</span>
              <img
                src="@/assets/images/pipeline.svg"
                class="nav-img"
                height="16px"
                alt=""
                style="margin-top: 0"
              />
            </label>
          </router-link>
  
          <router-link
            v-if="(isTeamLead || isAdmin) && userCRM"
            class="side-wrapper"
            exact-active-class="active"
            :to="{ name: 'Forms' }"
          >
            <label class="side-icon side-workflow" style="margin: 8px 0 0 0">
              <span class="side-tooltip-single" style="top: -5px; width: 170px"
                >{{ userCRM === 'SALESFORCE' ? 'Salesforce' : 'Hubspot' }} field mapping</span
              >
              <img
                src="@/assets/images/edit-note.svg"
                class="nav-img"
                height="16px"
                alt=""
                style="margin-top: 0"
              />
            </label>
          </router-link>
  
          <router-link
            v-if="userCRM === 'SALESFORCE'"
            class="side-wrapper"
            exact-active-class="active"
            :to="{ name: 'Meetings' }"
          >
            <label class="side-icon side-workflow" style="margin: 8px 0 0 0">
              <span class="side-tooltip-single" style="top: -5px; width: 75px">Meetings</span>
              <img
                src="@/assets/images/calendar.svg"
                class="nav-img"
                height="16px"
                alt=""
                style="margin-top: 0"
              />
            </label>
          </router-link>
  
          <router-link
            class="side-wrapper"
            exact-active-class="active"
            :to="{ name: 'Integrations' }"
          >
            <label class="side-icon side-workflow" style="margin: 8px 0 0 0">
              <span class="side-tooltip-single" style="top: -5px">Integrations</span>
              <img
                src="@/assets/images/connect.svg"
                class="nav-img"
                height="16px"
                alt=""
                style="margin-top: 0"
              />
            </label>
          </router-link>
          <router-link
            class="side-wrapper"
            exact-active-class="active"
            v-if="routeName === 'InviteUsers' && userCRM"
            :to="{ name: 'InviteUsers' }"
          >
            <label class="side-icon side-workflow" style="margin: 8px 0 0 0">
              <span class="side-tooltip-single" style="top: -5px; width: 190px"
                >Profile & Team Management</span
              >
              <img
                src="@/assets/images/profile.svg"
                class="nav-img"
                height="16px"
                alt=""
                style="margin-top: 0"
              />
            </label>
          </router-link>
  
          <router-link
            class="side-wrapper"
            exact-active-class="active"
            v-else-if="userCRM"
            :to="{ name: 'InviteUsers' }"
          >
            <label class="side-icon side-workflow" style="margin: 8px 0 0 0">
              <span class="side-tooltip-single" style="top: -5px; width: 190px"
                >Profile & Team Management</span
              >
              <img
                src="@/assets/images/profile.svg"
                class="nav-img"
                height="16px"
                alt=""
                style="margin-top: 0"
              />
            </label>
          </router-link>
  
          <div @mouseenter="openModal()" style="margin-left: 2px" class="side-wrapper">
            <label class="side-icon side-workflow" style="">
             
              <img
                src="@/assets/images/chat.svg"
                class="side-img"
                style="margin-top: 0"
                height="16px"
                alt=""
              />
            </label>
          </div>
  
          <router-link
            class="side-wrapper"
            exact-active-class="active"
            :to="{ name: 'DemoCenter' }"
            style="margin-top: auto; margin-bottom: -4px; padding-left: 9px; margin-left: 4px"
          >
            <label class="side-icon side-workflow" style="margin: 8px 0 0 0">
              <span class="side-tooltip-single" style="top: -5px; width: 100px">Demo Center</span>
              <img
                src="@/assets/images/play-alt.svg"
                class=""
                height="16px"
                alt=""
                style="margin-top: 0; filter: invert(40%)"
              />
            </label>
          </router-link>
          <div style="margin-left: 2px" class="side-wrapper">
            <label class="side-icon side-workflow" style="">
              <span class="side-tooltip"
                ><div>Need help?</div>
                <div>Email: cx@mymanagr.com</div></span
              >
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
            <div style="margin-left: 5px">
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
          <router-link :to="{ name: 'Login' }" style="position: absolute; bottom: 3%; left: 3%;">
            <div style="margin-left: 5px">
              <img @click="logOut" src="@/assets/images/logout.svg" alt="" height="16px" />
            </div>
          </router-link>
        </div>
      </nav> -->
    </div>
  </div>
</template>

<script>
import { CollectionManager } from '@thinknimble/tn-models'
import { decryptData } from '../encryption'

export default {
  name: 'NavBar',
  components: {
    CollectionManager,
    Modal: () => import(/* webpackPrefetch: true */ '@/components/InviteModal'),
  },
  data() {
    return {
      items: [],
      modalOpen: false,
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
    test(log) {
      console.log('log', log)
    },
    logOut() {
      this.$store.dispatch('logoutUser')
      this.$router.push({ name: 'Login' })
      // localStorage.isLoggedOut = true
    },
    openModal() {
      this.modalOpen = true
    },
    closeModal() {
      this.modalOpen = false
    },
  },
  computed: {
    isOnboarding() {
      // const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
      return this.$store.state.user.onboarding
    },
    isPR() {
      return this.$store.state.user.role === 'PR'
    },
    isPaid() {
      // const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
      return !!this.$store.state.user.organizationRef.isPaid
      return !!this.$store.state.user.organizationRef.isPaid
    },
    userIsLoggedIn() {
      return this.$store.getters.userIsLoggedIn
    },
    userCRM() {
      // const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
      return this.$store.state.user.crm
    },
    routeName() {
      return this.$route.name
    },
    isAdmin() {
      // const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
      return this.userIsLoggedIn && this.$store.state.user.isAdmin
    },
    isTeamLead() {
      // const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
      return this.userIsLoggedIn && this.$store.state.user.isTeamLead
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/modals';

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
div > span {
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

.command-modal {
  @include wide-modal();
  overflow-x: hidden;
  height: 100%;
  align-items: center;
  padding: 0px 24px 24px 24px;
  position: relative;
  color: $base-gray;

  header {
    position: sticky;
    top: 0;
    padding-top: 24px;
    background-color: white;
    display: flex;
    flex-direction: row;
    align-items: flex-start;
    justify-content: space-between;
    width: 100%;
    border-bottom: 1px solid $soft-gray;
    h2 {
      text-align: left;
      font-weight: normal;
      letter-spacing: 0.3px;
      padding: 0;
      margin: 0;
    }
    p {
      letter-spacing: 0.3px;
      font-size: 13px;
      padding: 0;
      color: $light-gray-blue;
    }
  }

  section {
    width: 100%;
    padding-top: 8px;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    justify-content: flex-start;

    div {
      margin: 0;
      border-bottom: 1px solid $soft-gray;
      width: 100%;
      padding: 12px 0px 0px 4px;
      h5 {
        margin: 0;
        font-size: 15px;
        font-weight: normal;
        span {
          font-weight: bold;
          letter-spacing: 0.3px;
          color: black;
        }
      }
      p {
        font-size: 14px;
        padding: 0;
        color: $light-gray-blue;
      }
    }
  }

  &__section {
    display: flex;
    flex-direction: row;
    align-items: center;

    button {
      background-color: $grape;
      color: white;
      height: 30px;
      width: auto;
      padding: 0 8px;
      display: flex;
      flex-direction: row;
      align-items: center;
      justify-content: center;
      gap: 6px;

      span {
        color: $mid-gray !important;
        padding: 0 2px;
      }
    }
  }

  footer {
    width: 100%;
    position: sticky;
    bottom: 0;
    margin-top: 16px;
    background-color: white;
    padding-bottom: 16px;
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;

    button {
      background-color: $dark-green;
      padding: 11px;
      font-size: 13px;
      border-radius: 4px;
      border: none;

      color: $white;
      cursor: pointer;
      transition: all 0.25s;
    }

    button:hover {
      box-shadow: 0 6px 6px rgba(0, 0, 0, 0.1);
      transform: scale(1.025);
    }
  }
}
.margin-customize {
  margin: 0.5rem 0 0 0.8rem;
}
</style>
