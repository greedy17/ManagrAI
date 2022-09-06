<template>
  <div style="margin-top: 3rem">
    <div class="sidenav">
      <router-link exact-active-class="active" :to="{ name: 'Required' }">
        <div class="tooltip">
          <img
            src="@/assets/images/optional.svg"
            class="invert"
            style="height: 1rem; margin-right: 1rem"
            alt=""
          />
          <span class="tooltiptext">Field Mapping</span>
        </div>
      </router-link>

      <router-link exact-active-class="active" :to="{ name: 'ValidationRules' }">
        <div class="tooltip">
          <img
            src="@/assets/images/gavel.svg"
            class="invert"
            style="height: 1rem; margin-right: 1rem"
            alt=""
          />
          <span class="tooltiptext">Validation Rules</span>
        </div>
      </router-link>
    </div>

    <router-view :key="$route.fullPath"></router-view>
  </div>
</template>

<script>
import { CollectionManager } from '@thinknimble/tn-models'
import { UserOnboardingForm } from '@/services/users/forms'
import User from '@/services/users'
import AlertTemplate from '@/services/alerts/'

export default {
  name: 'CustomizeLandingPage',
  components: {
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

@keyframes tooltips-horz {
  to {
    opacity: 0.975;
    transform: translate(10%, 0%);
  }
}

img {
  filter: invert(90%);
  margin-left: 0.5rem;
}

.sidenav {
  height: 100%;
  width: 64px;
  font-size: 0.85rem;
  position: fixed;
  left: 0;
  background-color: #fafbfc;
  border-right: 2px solid $soft-gray;
  color: $gray;
  padding: 24px 6px;
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
    filter: invert(99%);
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
    filter: invert(99%);
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

.invert {
  filter: invert(40%);
  height: 20px !important;
}
.tooltip {
  position: relative;
  height: 2.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 20px 0px;
}
.tooltip .tooltiptext {
  visibility: hidden;
  width: 160px;
  background-color: $base-gray;
  color: white;
  text-align: center;
  border: none !important;

  letter-spacing: 0.5px;
  padding: 6px 0;
  border-radius: 6px;
  font-size: 12px;

  /* Position the tooltip text */
  position: absolute;
  z-index: 1;
  top: 6px;
  left: 215%;
  margin-left: -60px;

  /* Fade in tooltip */
  opacity: 0;
  transition: opacity 0.3s;
}

/* Tooltip arrow */

// .tooltip .tooltiptext::after {
//   content: ' ';
//   position: absolute;
//   top: 50%;
//   right: 100%; /* To the left of the tooltip */
//   margin-top: -6px;
//   border-width: 4px;
//   border-style: solid;
//   border-color: transparent black transparent transparent;
// }

.tooltip:hover .tooltiptext {
  visibility: visible;
  animation: tooltips-horz 300ms ease-out forwards;
}
</style>

