<template>
  <div class="page">
    <div class="page__main-content-area" style="padding: 1rem">
      <router-view :key="$route.fullPath"></router-view>
    </div>
  </div>
</template>

<script>
import { decryptData } from '../../encryption'

export default {
  name: 'Settings',
  created() {},
  computed: {
    isStaff() {
      // used to check superuser if is staff then they currently do not have an org
      const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
      return decryptedUser.isStaff
    },
    organization() {
      const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
      return decryptedUser.organizationRef && decryptedUser.organizationRef.name
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

a {
  text-decoration: none;
}
</style>
