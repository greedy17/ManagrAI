<template>
  <div>
    <div v-if="!isAdmin" class="sidenav">
      <div style="margin-bottom: 2rem; margin-left: 0.5rem">
        <h3 class="title">Workflow Automations</h3>
        <h5 style="margin-top: -0.65rem; color: #9b9b9b">Where Salesforce meets Slack</h5>
      </div>

      <router-link
        v-if="user.userLevel !== 'MANAGER'"
        exact-active-class="active"
        :to="{ name: 'CreateNew' }"
      >
        <div :class="isOnboarding ? 'onboarding row' : 'row'">
          <img
            src="@/assets/images/trophy.png"
            style="height: 1.3rem; margin-right: 1rem; padding-left: 0.5rem"
            alt=""
          />
          <h5 v-if="user.userLevel === 'REP'">Popular</h5>
        </div>
      </router-link>

      <div style="background-color: #ebfcf3; border-radius: 0.3rem; margin-bottom: 0.25rem" v-else>
        <div
          @click="isPopular()"
          style="cursor: pointer"
          :class="isOnboarding ? 'onboarding row' : 'row'"
        >
          <img src="@/assets/images/trophy.png" style="height: 1rem; margin-right: 0.5rem" alt="" />

          <h3>Popular</h3>
          <img
            src="@/assets/images/dropdown.png"
            style="height: 1.25rem; margin-top: 0.25rem"
            alt=""
          />
        </div>

        <div v-if="popular" style="margin-left: 1.5rem; margin-top: -0.75rem" class="col">
          <router-link exact-active-class="active" :to="{ name: 'RealTime' }">
            <div :class="isOnboarding ? 'onboarding row' : 'row'">
              <img
                src="@/assets/images/bolt.png"
                style="height: 0.9rem; margin-right: 0.25rem"
                alt=""
              />
              <h5>Instant Updates</h5>
            </div>
          </router-link>
          <router-link
            style="margin-top: -2rem"
            exact-active-class="active"
            :to="{ name: 'CreateNew' }"
          >
            <div style="margin-top: -1rem" :class="isOnboarding ? 'onboarding row' : 'row'">
              <img
                src="@/assets/images/org.png"
                style="height: 0.8rem; margin-right: 0.25rem"
                alt=""
              />

              <h5>Pipeline Management</h5>
            </div>
          </router-link>
        </div>
      </div>

      <div
        v-if="isOnboarding && user.activatedManagrConfigs.includes('Update Forecast')"
        style="margin-bottom: -0.5rem"
        class="bouncy"
        id="toolTip"
      >
        <p>
          Onboarding Complete! Visit the tab below to run, edit, or delete workflows. You can also
          stay on this page to activate more worklows.
        </p>
        <div id="tailShadow"></div>
        <div id="tail1"></div>
        <div id="tail2"></div>
      </div>
      <router-link
        v-if="isOnboarding"
        :class="
          isOnboarding && !user.activatedManagrConfigs.includes('Update Forecast')
            ? 'onboarding row'
            : 'row'
        "
        exact-active-class="active"
        :to="{ name: 'ListTemplates' }"
      >
        <div class="row">
          <img
            src="@/assets/images/star.png"
            style="height: 1.3rem; margin-right: 1rem; padding-left: 0.5rem"
            alt=""
          />
          <h5 @click="onboardComplete">
            Saved
            <span style="margin-left: 0.25rem" class="counter">{{
              alertsCount(templates.list.length)
            }}</span>
          </h5>
        </div>
      </router-link>
      <router-link v-else exact-active-class="active" :to="{ name: 'ListTemplates' }">
        <div class="row">
          <img
            src="@/assets/images/star.png"
            style="height: 1.3rem; margin-right: 1rem; padding-left: 0.5rem"
            alt=""
          />
          <h5>
            Saved
            <span style="margin-left: 0.5rem" class="counter">{{
              alertsCount(templates.list.length)
            }}</span>
          </h5>
        </div>
      </router-link>

      <router-link exact-active-class="active" :to="{ name: 'BuildYourOwn' }">
        <div :class="isOnboarding ? 'onboarding row' : 'row'">
          <img
            src="@/assets/images/build.png"
            style="height: 1.2rem; margin-right: 1rem; padding-left: 0.5rem"
            alt=""
          />
          <h5>Custom</h5>
        </div>
      </router-link>

      <div :class="isOnboarding ? 'onboarding row' : 'row'" style="cursor: not-allowed">
        <img
          src="@/assets/images/sharing.png"
          style="height: 1.3rem; margin-right: 1rem; padding-left: 0.5rem"
          alt=""
        />
        <h5>Shared<span class="coming-soon">coming soon</span></h5>
      </div>
    </div>

    <div v-else class="sidenav sidenav__background">
      <div style="margin-bottom: 2rem; margin-left: 0.5rem">
        <h3 class="title">Workflow Automations</h3>
        <h5 style="margin-top: -0.65rem; color: #9b9b9b">Let us do the work for you</h5>
      </div>

      <div style="background-color: #ebfcf3; border-radius: 0.3rem; margin-bottom: 0.25rem">
        <div @click="isPopular()" style="cursor: pointer" class="row">
          <img src="@/assets/images/trophy.png" style="height: 1rem; margin-right: 0.5rem" alt="" />

          <h3>Popular</h3>
          <img
            src="@/assets/images/dropdown.png"
            style="height: 1.25rem; margin-top: 0.25rem"
            alt=""
          />
        </div>

        <div v-if="popular" style="margin-top: -0.25rem" class="col">
          <router-link exact-active-class="active" :to="{ name: 'RealTime' }">
            <div style="height: 2.25rem" class="row">
              <img
                src="@/assets/images/bolt.png"
                style="height: 0.9rem; margin-right: 0.25rem; margin-left: 1rem"
                alt=""
              />
              <h5 style="margin-left: 1rem">Instant Updates</h5>
            </div>
          </router-link>
          <router-link
            style="margin-top: -2rem"
            exact-active-class="active"
            :to="{ name: 'CreateNew' }"
          >
            <div style="margin-top: -0.25rem; height: 2.25rem" class="row">
              <img
                src="@/assets/images/org.png"
                style="height: 0.8rem; margin-right: 0.25rem; margin-left: 1rem"
                alt=""
              />

              <h5 style="margin-left: 1rem">Pipeline Management</h5>
            </div>
          </router-link>
        </div>
      </div>

      <router-link exact-active-class="active" :to="{ name: 'ListTemplates' }">
        <div class="row">
          <img
            src="@/assets/images/star.png"
            style="height: 1.3rem; margin-right: 1rem; padding-left: 0.5rem"
            alt=""
          />
          <h5>
            Saved
            <span style="margin-left: 0.5rem" class="counter">{{
              alertsCount(templates.list.length)
            }}</span>
          </h5>
        </div>
      </router-link>

      <router-link exact-active-class="active" :to="{ name: 'BuildYourOwn' }">
        <div class="row">
          <img
            src="@/assets/images/build.png"
            style="height: 1.2rem; margin-right: 1rem; padding-left: 0.5rem"
            alt=""
          />
          <h5>Custom</h5>
        </div>
      </router-link>

      <div class="row" style="cursor: not-allowed">
        <img
          src="@/assets/images/sharing.png"
          style="height: 1.3rem; margin-right: 1rem; padding-left: 0.5rem"
          alt=""
        />
        <h5>Shared<span class="coming-soon">coming soon</span></h5>
      </div>
    </div>

    <router-view :key="$route.fullPath"></router-view>
  </div>
</template>

<script>
import SlackMessagePreview from '@/views/settings/alerts/create/SlackMessagePreview'
import { CollectionManager, Pagination } from '@thinknimble/tn-models'
import { UserOnboardingForm } from '@/services/users/forms'
import User from '@/services/users'
import AlertTemplate, {
  AlertGroupForm,
  AlertTemplateForm,
  AlertConfigForm,
  AlertMessageTemplateForm,
  AlertOperandForm,
} from '@/services/alerts/'

export default {
  name: 'AlertsDashboardMenu',
  components: {
    SlackMessagePreview,
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
    handleUpdate() {
      this.loading = true
      User.api
        .update(this.user.id, this.userOnboardingForm.value)
        .then((response) => {
          this.$store.dispatch('updateUser', User.fromAPI(response.data))
        })
        .catch((e) => {
          console.log(e)
        })
      this.$router.push({ name: 'ListTemplates' })
    },
    alertsCount(num) {
      let int = num
      if (this.hasZoomChannel) {
        int++
      }
      if (this.hasRecapChannel) {
        int++
      }
      return int
    },
    onboardComplete() {
      this.userOnboardingForm.field.onboarding.value = false
      this.handleUpdate()
    },
    isPopular() {
      this.popular = !this.popular
    },
  },
  computed: {
    listLength() {
      return this.templates.list.length
    },
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
    isHome() {
      return this.$route.name == 'alerts'
    },
    isAdmin() {
      return this.$store.state.user.isAdmin
    },
    user() {
      return this.$store.state.user
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
.bouncy {
  animation: bounce 0.2s infinite alternate;
}
.onboarding {
  filter: blur(10px);
}
#toolTip {
  position: relative;
}

#toolTip p {
  color: $panther;
  font-weight: bold;
  padding: 10px;
  background-color: #f9f9f9;
  border: 2px solid $dark-green;
  -moz-border-radius: 5px;
  -ie-border-radius: 5px;
  -webkit-border-radius: 5px;
  -o-border-radius: 5px;
  border-radius: 5px;
}

#tailShadow {
  position: absolute;
  bottom: -8px;
  left: 88px;
  width: 0;
  height: 0;
  border: solid 2px $dark-green;
  box-shadow: 0 0 10px 1px #555;
}
h3 {
  font-size: 1.2rem;
}
h5 {
  font-size: 0.8rem;
  font-weight: 700px;
}
#tail1 {
  position: absolute;
  bottom: -20px;
  left: 80px;
  width: 0;
  height: 0;
  border-color: $dark-green transparent transparent transparent;
  border-width: 10px;
  border-style: solid;
}

#tail2 {
  position: absolute;
  bottom: -18px;
  left: 80px;
  width: 0;
  height: 0;
  border-color: #f9f9f9 transparent transparent transparent;
  border-width: 10px;
  border-style: solid;
}
img {
  filter: invert(90%);
  margin-left: 0.5rem;
}
.coming-soon {
  @include muted-font(13px);
}
.center {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
}
.counter {
  border: 2px solid $base-gray;
  border-radius: 0.3rem;
  padding: 0.1rem 0.3rem;
  font-size: 0.75rem;
  color: $base-gray;
}
.sidenav {
  height: 100%;
  width: 18vw;
  font-size: 0.85rem;
  position: fixed;
  left: 0;
  background-color: #fafbfc;
  border-right: 3px solid $soft-gray;
  color: $base-gray;
  overflow-x: hidden;
  padding: 1rem;
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
.active div {
  color: $darker-green;
  background-color: $lighter-green;
  border-radius: 0.3rem;
  font-weight: bold;
  position: relative;
}
.active div:after {
  content: '';
  background: $darker-green;
  position: absolute;
  bottom: 0.65rem;
  left: 0;
  height: 50%;
  width: 3px;
}
a:hover div {
  background-color: $lighter-green;
  color: $darker-green;
  border-radius: 0.3rem;
  img {
    filter: none;
  }
}
a:hover span {
  border-color: $darker-green;
  color: $darker-green;
}
.active img {
  filter: none;
}
.active span {
  border-color: $darker-green;
  color: $darker-green;
}
.title {
  color: $base-gray;
  font-weight: bold;
}
.row {
  display: flex;
  flex-direction: row;
  height: 3rem;
  align-items: center;
  margin-top: 0.1rem;
  margin-bottom: 0.1rem;
}
</style>
