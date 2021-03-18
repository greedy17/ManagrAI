<template>
  <div class="notifications">
    <div class="notifications__header__container">
      <div class="notifications__header__title">Customize your Notifications and Alerts</div>
      <div class="notifications__header__container__text">
        <div class="notifications__header__text">Coming Soon...</div>
        <div class="notifications__header__text">Invite and Customize your Team</div>
      </div>
    </div>
    <div class="notifications__body__container">
      <div class="notifications__body">
        <div class="notifications__body__section__left">
          <div class="notifications__body__section__left__title">Automated Assistance</div>
        </div>
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

  &__body {
    width: 60%;

    margin: 45px 108px 1px 35px;
    padding: 25px 17px 32px 39.6px;
    border-radius: 5px;
    box-shadow: 0 5px 10px 0 rgba(132, 132, 132, 0.26);
    border: solid 2px #dcdddf;
    background-color: #ffffff;
    left: 13rem;
    top: -6rem;
    min-height: 70vh;
    &__container {
      display: flex;
      justify-content: center;
    }

    &__section {
    }
  }
}
</style>

