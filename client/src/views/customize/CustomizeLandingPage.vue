<template>
  <div style="margin-top: 4rem">
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
        <h3 class="title">Manage Actions</h3>
        <h5 style="margin-top: -0.5rem">Where Salesforce meets Slack</h5>
      </div>
      <router-link exact-active-class="active" :to="{ name: 'Required' }">
        <div class="row">
          <img src="@/assets/images/warning.png" style="height: 1rem; margin-right: 1rem" alt="" />
          <h5>Required</h5>
        </div>
      </router-link>

      <router-link exact-active-class="active" :to="{ name: 'Custom' }">
        <div class="row">
          <img src="@/assets/images/optional.png" style="height: 1rem; margin-right: 1rem" alt="" />
          <h5>Optional</h5>
        </div>
      </router-link>

      <router-link exact-active-class="active" :to="{ name: 'ValidationRules' }">
        <div class="row">
          <img src="@/assets/images/gavel.png" style="height: 1rem; margin-right: 1rem" alt="" />
          <h5>Validation Rules</h5>
        </div>
      </router-link>
    </div>

    <router-view :key="$route.fullPath"></router-view>
  </div>
</template>

<script>
import SlackMessagePreview from '@/views/settings/alerts/create/SlackMessagePreview'
import { CollectionManager } from '@thinknimble/tn-models'
import { UserOnboardingForm } from '@/services/users/forms'
import User from '@/services/users'
import AlertTemplate from '@/services/alerts/'

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
  },
  computed: {
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
  width: 15.5vw;
  font-size: 0.85rem;
  position: fixed;
  left: 0;
  background-color: #fafbfc;
  border-right: 2px solid $soft-gray;
  color: $gray;
  overflow-x: hidden;
  padding: 1rem;
  margin-top: -1.5rem;
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
.active div:hover {
  img {
    filter: none;
  }
  color: white;
}
.active div {
  color: $base-gray;
  background-color: $dark-green;
  border-radius: 0.2rem;
  font-weight: bold;
  position: relative;
  color: white;
  img {
    filter: none;
  }
}
.active div:after {
  content: '';
  background: $darker-green;
  position: absolute;
  bottom: 0.4rem;
  left: 0;
  height: 70%;
  width: 3px;
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
  margin-bottom: 0.25rem;
  padding-left: 0.5rem;
  height: 2.5rem;
}
.row:hover {
  img {
    filter: brightness(0%) saturate(100%) invert(63%) sepia(31%) saturate(743%) hue-rotate(101deg)
      brightness(93%) contrast(89%);
  }
  color: $dark-green;
}
</style>

