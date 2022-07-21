<template>
  <div>
    <div v-if="userLevel == 'REP' && !isOnboarding" class="sidenav">
      <!-- <div style="margin-bottom: 2rem; margin-left: 0.5rem">
        <h4 class="title">Workflow Automations</h4>
        <h5 style="margin-top: -0.65rem; color: #9b9b9b">Let us do the work for you</h5>
      </div> -->

      <router-link exact-active-class="active" :to="{ name: 'CreateNew' }">
        <div class="tooltip">
          <img
            src="@/assets/images/org.svg"
            class="invert"
            style="height: 1.2rem; margin-right: 1rem; margin-left: 1rem"
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
            height="20px"
            style="margin-right: 1rem; padding-left: 0.25rem"
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
            style="height: 1.2rem; margin-right: 1rem; padding-left: 0.5rem"
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
      <!-- <div style="margin-bottom: 2rem; margin-left: 0.5rem">
        <h4 class="title">Workflow Automations</h4>
        <h5 style="margin-top: -0.65rem; color: #9b9b9b">Let us do the work for you</h5>
      </div> -->

      <router-link exact-active-class="active" :to="{ name: 'CreateNew' }">
        <div class="tooltip">
          <img
            src="@/assets/images/org.svg"
            class="invert"
            style="height: 1.2rem; margin-right: 1rem; margin-left: 1rem"
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
            height="20px"
            style="margin-right: 1rem; padding-left: 0.25rem"
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
            style="height: 1.2rem; margin-right: 1rem; padding-left: 0.5rem"
            alt=""
          />
          <span class="tooltiptext">Custom Workflows</span>
        </div>
      </router-link>
    </div>

    <div v-else-if="userLevel == 'MANAGER'" class="sidenav sidenav__background">
      <!-- <div style="margin-bottom: 2rem; margin-left: 0.5rem">
        <h4 class="title">Workflow Automations</h4>
        <h5 style="margin-top: -0.65rem; color: #9b9b9b">Let us do the work for you</h5>
      </div> -->

      <router-link exact-active-class="active" :to="{ name: 'RealTime' }">
        <div class="tooltip">
          <img
            class="invert"
            src="@/assets/images/bolt.svg"
            style="height: 0.9rem; margin-right: 1rem; margin-left: 1rem"
            alt=""
          />
          <span class="tooltiptext">Instant Updates</span>
        </div>
        <!-- <h5>Instant Updates</h5> -->
      </router-link>

      <router-link exact-active-class="active" :to="{ name: 'CreateNew' }">
        <div class="tooltip">
          <img
            src="@/assets/images/org.svg"
            class="invert"
            style="height: 1.2rem; margin-right: 1rem; margin-left: 1rem"
            alt=""
          />
          <span class="tooltiptext">Popular Workflows</span>
          <!-- <h5>Popular Workflows</h5> -->
        </div>
      </router-link>

      <router-link exact-active-class="active" :to="{ name: 'ListTemplates' }">
        <div class="tooltip">
          <img
            src="@/assets/images/star.svg"
            class="invert"
            height="20px"
            style="margin-right: 1rem; padding-left: 0.25rem"
            alt=""
          />
          <span class="tooltiptext">Active Workflows</span>
          <!-- <h5>Active Workflows</h5> -->
        </div>
      </router-link>

      <router-link exact-active-class="active" :to="{ name: 'BuildYourOwn' }">
        <div class="tooltip">
          <img
            class="invert"
            src="@/assets/images/build.svg"
            style="height: 1.2rem; margin-right: 1rem; padding-left: 0.5rem"
            alt=""
          />
          <span class="tooltiptext">Custom Workflows</span>
          <!-- <h5>Custom</h5> -->
        </div>
      </router-link>
    </div>

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
.sidenav {
  height: 100%;
  width: 62px;
  font-size: 14px;
  position: fixed;
  left: 0;
  background-color: #fafbfc;
  border-right: 2px solid $soft-gray;
  color: $base-gray;
  padding: 6px;
  margin-top: -1rem;
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
.active div:hover {
  color: white;
  img {
    filter: invert(99%);
  }
}
.active div {
  color: white;
  background-color: $dark-green;
  border-radius: 0.2rem;
  font-weight: bold;
  position: relative;
  img {
    filter: invert(99%);
  }
  span {
    color: white !important;
    border: 1px solid white !important;
  }
}
.active div:after {
  content: '';
  background: $darker-green;
  position: absolute;
  bottom: 0.3rem;
  left: 0;
  height: 70%;
  width: 3px;
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
  height: 20px !important;
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
  height: 2.25rem;
  align-items: center;
  margin-top: 0.5rem;
  margin-bottom: 0.5rem;
}
.tooltip {
  position: relative;
  height: 2.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 16px 0px;
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
  top: 8px;
  left: 215%;
  margin-left: -60px;
  opacity: 70%;
  transition: opacity 0.3s;
}

.tooltip:hover .tooltiptext {
  visibility: visible;
  animation: tooltips-horz 300ms ease-out forwards;
}

// [tooltiptext][flow^='left']:hover::before,
// [tooltiptext][flow^='left']:hover::after,
// [tooltiptext][flow^='right']:hover::before,
// [tooltiptext][flow^='right']:hover::after {
//   animation: tooltips-horz 300ms ease-out forwards;
// }
</style>
