<template>
  <div class="notifications">
    <div class="notifications__header__container">
      <div class="notifications__header__title">Customize your Notifications and Alerts</div>
      <div class="notifications__header__container__text">
        <div class="notifications__header__text">Coming Soon...</div>
        <div class="notifications__header__text">Invite and Customize your Team</div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Notifications',
  data() {
    return {
      isAdmin: null,
    }
  },
  created() {
    const user = this.$store.state.user
    this.isAdmin = user.isAdmin
  },
}
</script>

<style lang="scss">
@import '@/styles/variables';

.notifications {
  &__header {
    &__container {
      display: flex;
      flex-direction: column;
      align-items: center;
      margin-top: 3rem;
      font-size: 1.25rem;

      &__text {
        display: flex;
        flex-direction: column;
        align-items: center;
        margin: 2rem 0;
        font-size: 14px;
      }
    }
    &__title {
      font-family: #{$bold-font-family};
    }
  }
}
</style>

