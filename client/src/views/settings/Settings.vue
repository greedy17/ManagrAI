<template>
  <div class="page">
    <div class="page__left-nav-bar" style="padding: 1rem;">
      <div class="toolbar">
        <div class="toolbar__header">
          <span class="toolbar__title">Settings</span>
          <h5 class="org-statement" v-if="organization">
            You're viewing settings for {{ organization }}
          </h5>
        </div>
        <router-link
          v-if="$store.state.user.userLevel == 'MANAGER' || $store.state.user.isAdmin"
          :to="{ name: 'Invite' }"
        >
          <div class="toolbar__row">
            Invite User
          </div>
        </router-link>

        <router-link :to="{ name: 'Profile' }">
          <div class="toolbar__row">
            Profile
          </div>
        </router-link>
        <router-link :to="{ name: 'Integrations' }">
          <div class="toolbar__row">
            Integrations
          </div>
        </router-link>
      </div>
    </div>
    <div class="page__main-content-area" style="padding: 1rem;">
      <router-view name="user-settings" :key="$route.fullPath"></router-view>
    </div>
  </div>
</template>

<script>
import User from '@/services/users'

import { objectToCamelCase, objectToSnakeCase } from '@thinknimble/tn-utils'

export default {
  name: 'Settings',
  created() {},
  computed: {
    isStaff() {
      // used to check superuser if is staff then they currently do not have an org
      return this.$store.state.user.isStaff
    },
    isManager() {
      return this.$store.state.user.type === User.types.MANAGER
    },
    organization() {
      return this.$store.state.user.organizationRef && this.$store.state.user.organizationRef.name
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/layout';
@import '@/styles/containers';
@import '@/styles/sidebars';
@import '@/styles/mixins/utils';

.toolbar__row {
  @include pointer-on-hover;
}

.org-statement {
  color: $mid-gray;
  margin-top: 1rem;
  margin-bottom: 0;
}
a {
  text-decoration: none;
}
::v-deep .router-link-exact-active.router-link-active {
  .toolbar__row {
    background-color: #e5f2ea;
    border-bottom: 4px #199e54 solid;
  }
}
</style>
