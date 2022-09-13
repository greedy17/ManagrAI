<template>
  <div class="alerts">
    <section class="wrapper">
      <div class="tabs">
        <div class="tab">
          <input type="radio" name="css-tabs" id="tab-1" checked class="tab-switch" />
          <label for="tab-1" class="tab-label" @click="goToActive">Workflows</label>
          <div class="tab-content">
            <router-view :key="$route.fullPath"></router-view>
          </div>
        </div>

        <div class="tab">
          <input type="radio" name="css-tabs" id="tab-2" class="tab-switch" />
          <label for="tab-2" class="tab-label" @click="goToCustom">Workflow Builder</label>
          <div class="tab-content">
            <router-view :key="$route.fullPath"></router-view>
          </div>
        </div>
      </div>
    </section>
    <!-- <div v-if="userLevel == 'REP' && !isOnboarding" class="sidenav">
      <h2>Workflows</h2>
      <router-link exact-active-class="active" :to="{ name: 'CreateNew' }">
        <div class="tooltip">
          <img
            src="@/assets/images/org.svg"
            class="invert"
            style="height: 14px; margin-right: 8px; margin-left: 1rem"
            alt=""
          />
          <span class="tooltiptext">Popular Workflows</span>
        </div>
      </router-link>
      <router-link exact-active-class="active" :to="{ name: 'ListTemplates' }">
        <div class="tooltip">
          <img
            src="@/assets/images/star.svg"
            class="invert"
            height="14px"
            style="margin-right: 8px; padding-left: 0.25rem"
            alt=""
          />
          <span class="tooltiptext">Active Workflows</span>
        </div>
      </router-link>

      <router-link exact-active-class="active" :to="{ name: 'BuildYourOwn' }">
        <div class="tooltip">
          <img
            class="invert"
            src="@/assets/images/build.svg"
            style="height: 14px; margin-right: 8px; padding-left: 0.5rem"
            alt=""
          />
          <span class="tooltiptext">Custom Workflows</span>
        </div>
      </router-link>
    </div>

    <div
      v-else-if="userLevel !== 'MANAGER' && userLevel !== 'REP'"
      class="sidenav sidenav__background"
    >
      <h2>Workflows</h2>
      <router-link exact-active-class="active" :to="{ name: 'CreateNew' }">
        <div class="tooltip">
          <img
            src="@/assets/images/org.svg"
            class="invert"
            style="height: 14px; margin-right: 8px; margin-left: 1rem"
            alt=""
          />
          <span class="tooltiptext">Popular Workflows</span>
        </div>
      </router-link>

      <router-link exact-active-class="active" :to="{ name: 'ListTemplates' }">
        <div class="tooltip">
          <img
            src="@/assets/images/star.svg"
            class="invert"
            height="14px"
            style="margin-right: 8px; padding-left: 0.25rem"
            alt=""
          />
          <span class="tooltiptext">Active Workflows</span>
        </div>
      </router-link>

      <router-link exact-active-class="active" :to="{ name: 'BuildYourOwn' }">
        <div class="tooltip">
          <img
            class="invert"
            src="@/assets/images/build.svg"
            style="height: 14px; margin-right: 8px; padding-left: 0.5rem"
            alt=""
          />
          <span class="tooltiptext">Custom Workflows</span>
        </div>
      </router-link>
    </div>

    <div v-else-if="userLevel == 'MANAGER'" class="sidenav sidenav__background">
      <div class="row">
        <img
          src="@/assets/images/workflows.svg"
          height="16px"
          style="filter: invert(20%); margin-right: 8px"
          alt=""
        />
        <h2>Workflows</h2>
      </div>

      <router-link exact-active-class="active" :to="{ name: 'ListTemplates' }">
        <div class="tooltip">
          <img
            src="@/assets/images/star.svg"
            class="invert"
            height="14px"
            style="margin-right: 8px; padding-left: 0.25rem"
            alt=""
          />
          <span class="tooltiptext">Active Workflows</span>
        </div>
      </router-link>

      <router-link exact-active-class="active" :to="{ name: 'CreateNew' }">
        <div class="tooltip">
          <img
            src="@/assets/images/org.svg"
            class="invert"
            style="height: 14px; margin-right: 8px; margin-left: 1rem"
            alt=""
          />
          <span class="tooltiptext">Popular Workflows</span>
        </div>
      </router-link>

      <router-link exact-active-class="active" :to="{ name: 'RealTime' }">
        <div class="tooltip">
          <img
            class="invert"
            src="@/assets/images/bolt.svg"
            style="height: 14px; margin-right: 8px; margin-left: 1rem"
            alt=""
          />
          <span class="tooltiptext">Instant Updates</span>
        </div>
      </router-link>

      <router-link exact-active-class="active" :to="{ name: 'BuildYourOwn' }">
        <div style="border-right: none" class="tooltip">
          <img
            class="invert"
            src="@/assets/images/build.svg"
            style="height: 14px; margin-right: 8px; padding-left: 0.5rem"
            alt=""
          />
          <span class="tooltiptext">Custom Workflows</span>
        </div>
      </router-link>
    </div> -->

    <router-view :key="$route.fullPath"></router-view>
  </div>
</template>

<script>
import { CollectionManager } from '@thinknimble/tn-models'
import { UserOnboardingForm } from '@/services/users/forms'
import AlertTemplate from '@/services/alerts/'

export default {
  name: 'AlertsDashboardMenu',
  components: {
    CollectionManager,
  },
  data() {
    return {
      templates: CollectionManager.create({ ModelClass: AlertTemplate }),
      userOnboardingForm: new UserOnboardingForm({}),
      test: true,
      popular: true,
    }
  },
  async created() {
    this.templates.refresh()
  },
  methods: {
    goToPopular() {
      this.$router.push({ name: 'CreateNew' })
    },
    goToActive() {
      this.$router.push({ name: 'ListTemplates' })
    },
    goToInstant() {
      this.$router.push({ name: 'RealTime' })
    },
    goToCustom() {
      this.$router.push({ name: 'BuildYourOwn' })
    },
    // alertsCount(num) {
    //   let int = num
    //   if (this.hasZoomChannel) {
    //     int++
    //   }
    //   if (this.hasRecapChannel) {
    //     int++
    //   }
    //   return int
    // },
  },
  computed: {
    hasZoomChannel() {
      if (this.hasSlack) {
        return this.$store.state.user.slackAccount.zoomChannel
      }
    },
    hasRecapChannel() {
      if (this.hasSlack) {
        return this.$store.state.user.slackAccount.recapChannel
      }
    },
    hasSlack() {
      return this.$store.state.user.slackAccount
    },
    isOnboarding() {
      return this.$store.state.user.onboarding
    },
    user() {
      return this.$store.state.user
    },
    userLevel() {
      return this.$store.state.user.userLevel
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

@keyframes bounce {
  0% {
    transform: translateY(0);
  }
  100% {
    transform: translateY(-6px);
  }
}

@keyframes tooltips-horz {
  to {
    opacity: 0.9;
    transform: translate(10%, 0%);
  }
}
.onboarding {
  filter: blur(10px);
}
h5 {
  font-size: 0.8rem;
  font-weight: 700px;
}
img {
  filter: invert(90%);
  margin-left: 0.5rem;
}
.counter {
  border: 1px solid $base-gray;
  border-radius: 0.2rem;
  padding: 0.125rem 0.4rem;
  font-size: 10px;
  color: $base-gray;
  margin-left: 1.5rem;
}
.alerts {
  padding-left: 16px;
}
.wrapper {
  width: 92.5vw;
  margin: 0 auto;
  font-size: 14px;
  letter-spacing: 0.75px;
}
.tabs {
  position: relative;
  margin: 16px 0;
  background: white;
  border-radius: 6px;
}
.tabs::before,
.tabs::after {
  content: '';
  display: table;
}
.tabs::after {
  clear: both;
}
.tab {
  float: left;
  margin-left: 8px;
}
.tab-switch {
  display: none;
}
.tab-label {
  position: relative;
  display: block;
  line-height: 2.75em;
  height: 3em;
  padding: 0 1.618em;
  color: $light-gray-blue;
  cursor: pointer;
  top: 0;
  transition: all 0.25s;
}
.tab-label:hover {
  top: -0.25rem;
  transition: top 0.25s;
}
.tab-content {
  width: 100%;
  min-height: 92vh;
  position: absolute;
  z-index: 1;
  top: 2.75em;
  left: 0;
  padding: 8px 24px;
  background: #fff;
  color: $base-gray;
  opacity: 0;
  transition: all 0.35s;
  overflow: scroll;
  border-radius: 6px;

  section {
    div {
      display: flex;
      flex-direction: row;
      align-items: center;
      justify-content: space-between;
    }

    section {
      border: 1px dashed $light-gray-blue;
      background-color: $off-white;
      border-radius: 6px;
      min-height: 30vh;
      margin-top: 16px;
    }
  }
}
.tab-switch:checked + .tab-label {
  background: #fff;
  color: $base-gray;
  border-bottom: 0;
  transition: all 0.35s;
  z-index: 1;
  top: -0.0625rem;
}
.tab-switch:checked + label + .tab-content {
  z-index: 2;
  opacity: 1;
  transition: all 0.35s;
}
.tab-text {
  color: $light-gray-blue;
  font-size: 14px;
  letter-spacing: 0.75px;
}
.sidenav {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-start;
  height: 66px;
  width: 100vw;
  font-size: 12px;
  position: fixed;
  top: 0;
  background-color: white;
  border-bottom: 1px solid $soft-gray;
  color: $base-gray;
  padding: 4px 12px;
  z-index: 20;
}
a {
  text-decoration: none;
  color: $base-gray;
  cursor: pointer;
}
a:hover {
  border-radius: 0.2rem;
  cursor: pointer;
}

.active div {
  color: $dark-green;
  border-radius: 0.2rem;
  font-weight: bold;
  position: relative;
  img {
    filter: brightness(0%) saturate(100%) invert(63%) sepia(31%) saturate(743%) hue-rotate(101deg)
      brightness(93%) contrast(89%);
  }
  span {
    color: $dark-green !important;
    border: 1px solid white !important;
  }
}

a:hover div {
  color: $dark-green;
  border-radius: 0.2rem;
  img {
    filter: brightness(0%) saturate(100%) invert(63%) sepia(31%) saturate(743%) hue-rotate(101deg)
      brightness(93%) contrast(89%);
  }
}
.invert {
  filter: invert(40%);
}
a:hover span {
  border-color: $dark-green;
  color: $dark-green;
}
.active span {
  border-color: white;
  color: $white;
}
.title {
  color: $base-gray;
  font-weight: bold;
}
.row {
  display: flex;
  flex-direction: row;
  height: 16px;
  align-items: center;
  padding-right: 12px;
  border-right: 2px solid $soft-gray;
}
.tooltip {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  padding-right: 12px;
  border-right: 2px solid $soft-gray;
}
// .tooltip .tooltiptext {
//   visibility: hidden;
//   width: 160px;
//   background-color: $base-gray;
//   color: white;
//   text-align: center;
//   border: none !important;
//   letter-spacing: 1px;
//   padding: 8px 0;
//   border-radius: 6px;
//   font-size: 12px;
//   font-weight: bold !important;
//   position: absolute;
//   z-index: 1;
//   top: 8px;
//   left: 215%;
//   margin-left: -60px;
//   opacity: 70%;
//   transition: opacity 0.3s;
// }

// .tooltip:hover .tooltiptext {
//   visibility: visible;
//   animation: bounce 300ms ease-out forwards;
// }
</style>
