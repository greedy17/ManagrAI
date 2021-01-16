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
          v-if="$store.state.user.isManager || $store.state.user.isStaff"
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
        <!-- NOTE (Bruno 6-18-2020) once we get password-reset-flow incorporated, we can add the Password page -->
        <!-- <router-link :to="{ name: 'Profile' }">
          <div class="toolbar__row">
            Profile
          </div>
        </router-link> -->
      </div>
    </div>
    <div class="page__main-content-area" style="padding: 1rem;">
      <router-view name="user-settings" :key="$route.fullPath"></router-view>
    </div>
  </div>
</template>

<script>
import { objectToCamelCase, objectToSnakeCase } from '@thinknimble/tn-utils'
export default {
  name: 'Settings',
  created() {
    // 2021-01-16 William: Disabled this because it was overrding the user who just registered.
    // let us = {
    //   id: '7cfd2353-942d-4ff7-a0ff-47be5ebde745',
    //   email: 'pari@thinknimble.com',
    //   full_name: ' ',
    //   first_name: '',
    //   last_name: '',
    //   organization: '45bb82fa-54bf-43cf-bc2a-153956348689',
    //   organization_ref: {
    //     id: '45bb82fa-54bf-43cf-bc2a-153956348689',
    //     datetime_created: '2021-01-14T18:43:00.987776Z',
    //     last_edited: '2021-01-14T18:43:00.987820Z',
    //     name: 'ThinkNimble',
    //     photo: null,
    //     state: 'ACTIVE',
    //     is_trial: false,
    //   },
    //   accounts_ref: [],
    //   is_active: true,
    //   is_invited: true,
    //   is_staff: false,
    //   is_admin: true,
    //   is_superuser: false,
    //   user_level: 'MANAGER',
    //   email_auth_link:
    //     'https://api.nylas.com/oauth/authorize?redirect_uri=http%3A%2F%2Flocalhost%3A8080%2Fnylas%2Fcallback%2F&response_type=code&login_hint=pari%40thinknimble.com&state=2d81f8cf-6c8b-4fb4-a435-f39649833f4b&scopes=email.read_only%2C+email.send&client_id=2th0vp5dkvmc1lkcvf41quqkf',
    //   email_auth_account: null,
    //   email_auth_account_ref: null,
    //   profile_photo: null,
    //   slack_ref: null,
    //   zoom_account: null,
    //   token: '2ae721bdcbcc995b26e637694ce5f289b6008e22',
    // }
    // let tok = '2ae721bdcbcc995b26e637694ce5f289b6008e22'
    // this.$store.commit('UPDATE_USER', objectToCamelCase(us))
    // this.$store.commit('UPDATE_USERTOKEN', tok)
    // this.$store.dispatch('refreshCurrentUser')
  },
  computed: {
    isStaff() {
      // used to check superuser if is staff then they currently do not have an org
      return this.$store.state.user.isStaff
    },
    isManager() {
      return this.$store.state.user.type === 'MANAGER'
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
