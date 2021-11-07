<template>
  <div>
    <div class="sidenav sidenav__background">
      <div>
        <h2 class="title">Workflow Automations</h2>
      </div>
      <router-link exact-active-class="active" :to="{ name: 'CreateNew' }">
        <div :class="user.onboarding ? 'onboarding row' : 'row'">
          <img src="@/assets/images/trophy.png" style="height: 1rem; margin-right: 0.5rem" alt="" />
          <h3>Popular Workflows <span style="margin-left: 0.25rem" class="counter">5</span></h3>
        </div>
      </router-link>

      <!-- <div v-if="user" id="toolTip">
        <p v-if="user.onboarding">
          Onboarding complete! We'll take it from here. Feel free to activate the rest of the
          workflows now or come back later.
        </p>
      </div> -->
      <div
        v-if="user.onboarding && user.activatedManagrConfigs.includes('Close Date Approaching')"
        style="margin-bottom: -0.5rem"
        class="bouncy"
        id="toolTip"
      >
        <p>
          Onboarding complete! We'll take it from here. Visit this tab to view, edit, or delete
          workflows.
        </p>
        <div id="tailShadow"></div>
        <div id="tail1"></div>
        <div id="tail2"></div>
      </div>
      <router-link
        v-if="user.onboarding"
        :class="
          !user.onboarding && user.activatedManagrConfigs.includes('Close Date approaching')
            ? 'onboarding row'
            : 'row'
        "
        exact-active-class="active"
        :to="{ name: 'ListTemplates' }"
      >
        <div class="row">
          <img src="@/assets/images/star.png" style="height: 1rem; margin-right: 0.5rem" alt="" />
          <h3 @click="onboardComplete">
            Saved Workflows
            <span style="margin-left: 0.25rem" class="counter">{{
              alertsCount(templates.list.length)
            }}</span>
          </h3>
        </div>
      </router-link>
      <router-link v-else exact-active-class="active" :to="{ name: 'ListTemplates' }">
        <div class="row">
          <img src="@/assets/images/star.png" style="height: 1rem; margin-right: 0.5rem" alt="" />
          <h3>
            Saved Workflows
            <span style="margin-left: 0.25rem" class="counter">{{
              alertsCount(templates.list.length)
            }}</span>
          </h3>
        </div>
      </router-link>

      <router-link exact-active-class="active" :to="{ name: 'BuildYourOwn' }">
        <div :class="user.onboarding ? 'onboarding row' : 'row'">
          <img src="@/assets/images/build.png" style="height: 1rem; margin-right: 0.5rem" alt="" />
          <h3>Customized Workflows</h3>
        </div>
      </router-link>

      <div>
        <div :class="user.onboarding ? 'onboarding row' : 'row'" style="cursor: not-allowed">
          <img
            src="@/assets/images/analyze.png"
            style="height: 1.25rem; margin-right: 0.5rem"
            alt=""
          />
          <h3>Analyze <span class="coming-soon">coming soon</span></h3>
        </div>
      </div>
    </div>

    <div v-if="isHome" style="margin-left: 6vw">
      <h2 class="center" style="color: white">Smart Alerts</h2>
      <p class="center" style="font-weight: bold; color: #beb5cc; margin-top: -0.5rem">
        Automated workflows that help keep you on track
      </p>

      <div class="center" style="margin-top: 2rem">
        <SlackMessagePreview />
        <!-- <p style="color: #3c3940; align-self: flex-end; width: 30%">Ex.</p> -->
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
      user: this.$store.state.user,
      userOnboardingForm: new UserOnboardingForm({}),
    }
  },
  async created() {
    this.templates.refresh()
    this.userOnboardingForm = new UserOnboardingForm({
      onboarding: this.user.onboarding,
    })
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
    },
    alertsCount(num) {
      if (this.hasZoomChannel) {
        return num + 1
      } else {
        return num
      }
    },
    onboardComplete() {
      this.userOnboardingForm.field.onboarding.value = false
      this.handleUpdate()
    },
  },
  computed: {
    hasZoomChannel() {
      return this.$store.state.user.slackAccount.zoomChannel
    },
    onboarding() {
      return this.$store.state.user.onboarding
    },
    isHome() {
      return this.$route.name == 'alerts'
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
  border: 2px solid white;
  border-radius: 0.3rem;
  padding: 0.1rem 0.3rem;
  font-size: 0.75rem;
}
.sidenav {
  height: 100%;
  width: 18vw;
  font-size: 0.85rem;
  position: fixed;
  z-index: 1;
  left: 0;
  background-color: $panther;
  border: 2px solid $panther-silver;
  border-radius: 0.25rem;
  color: $panther-silver;
  overflow-x: hidden;
  padding-top: 20px;
  padding: 1rem;
  border-radius: 0.5rem;
}
a {
  text-decoration: none;
  font-weight: bold;
  color: $panther-silver;
  cursor: pointer;
}
a:hover {
  color: white;
  cursor: pointer;
}
.active div {
  color: white;
  background-color: $dark-green;
  border-radius: 0.25rem;
  padding: 0 0.3rem;
  font-weight: bold;
  margin-left: -0.35rem;
}
.title {
  color: white;
  font-weight: bold;
}
.row {
  display: flex;
  flex-direction: row;
  align-items: center;
}
</style>
