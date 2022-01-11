<template>
  <div>
    <div class="sidenav">
      <div
        style="
          margin-bottom: 1rem;
          margin-left: 0.5rem;
          display: flex;
          flex-direction: column;
          justify-content: flex-start;
        "
      >
        <!-- <img src="@/assets/images/map.png" style="height: 1.5rem" alt="" /> -->
        <h2 class="title">Field Mapping</h2>
        <h5 style="margin-top: -0.5rem">Where Salesforce meets Slack</h5>
      </div>
      <router-link exact-active-class="active" :to="{ name: 'Required' }">
        <div class="row">
          <img
            src="@/assets/images/warning.png"
            style="height: 1.25rem; margin-right: 1rem"
            alt=""
          />
          <h4>Required</h4>
        </div>
      </router-link>

      <router-link exact-active-class="active" :to="{ name: 'Custom' }">
        <div class="row">
          <img
            src="@/assets/images/optional.png"
            style="height: 1.25rem; margin-right: 1rem"
            alt=""
          />
          <h4>Optional</h4>
        </div>
      </router-link>

      <router-link exact-active-class="active" :to="{ name: 'ValidationRules' }">
        <div class="row">
          <img src="@/assets/images/gavel.png" style="height: 1.25rem; margin-right: 1rem" alt="" />
          <h4>Validation Rules</h4>
        </div>
      </router-link>
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
  name: 'CustomizeLandingPage',
  components: {
    SlackMessagePreview,
    CollectionManager,
  },
  data() {
    return {
      templates: CollectionManager.create({ ModelClass: AlertTemplate }),
      userOnboardingForm: new UserOnboardingForm({}),
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

img {
  filter: invert(90%);
  margin-left: 0.5rem;
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
  left: 0;
  background-color: #fafbfc;
  border-right: 3px solid $soft-gray;
  color: $gray;
  overflow-x: hidden;
  padding: 1rem;
  margin-top: -1rem;
}
a {
  text-decoration: none;
  font-weight: bold;
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
  bottom: 0.5rem;
  left: 0;
  height: 60%;
  width: 2px;
}
.active img {
  filter: none;
}
.title {
  color: $base-gray;
  font-weight: bold;
}
.row {
  display: flex;
  flex-direction: row;
  align-items: center;
  margin-top: 0.1rem;
  margin-bottom: 0.1rem;
  height: 3rem;
}
.row:hover {
  background-color: $lighter-green;
  color: $darker-green;
  border-radius: 0.3rem;
  img {
    filter: none;
  }
}
</style>

