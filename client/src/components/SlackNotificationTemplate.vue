<template>
  <div class="slack-notif">
    <div class="slack-notif__container">
      <div class="slack-notif__container-icon">
        <!-- vertical icon -->
      </div>
      <div class="slack-notif__container-content">
        <!-- horizontal stacked divs -->
        <div class="slack-notif__container-content__heading">
          <!--Horizontal spans -->
          <span class="slack-notif__container-content__heading-title">
            Managr
          </span>
          <span class="slack-notif__container-content__heading-type">
            APP
          </span>
          <span class="slack-notif__container-content__heading-time">
            {{ new Date() | timeOnlyShort }}
          </span>
        </div>
        <div class="slack-notif__container-content__body">
          {{ msg }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SlackNotificationTemplate',
  props: {
    msg: String,
    active: {
      type: Boolean,
      default: true,
    },
  },
}
</script>

<style scoped lang="scss">
@import '@/styles/variables';
@import '@/styles/mixins/utils';
.slack-notif {
  box-shadow: 0.2rem 0.5rem 0.5rem 0.2rem whitesmoke, -0.2rem 0.5rem 0.5rem 0.2rem whitesmoke;
  height: 5rem;
  padding: 0.8rem 2rem;
  border-radius: 1rem;
  width: 100%;
}
.slack-notif__container {
  display: flex;
  &-icon {
    background-image: url(../assets/images/slack.png);
    background-repeat: no-repeat;
    background-size: contain;
    background-position: center;
    height: 3rem;
    width: 5rem;
  }
  &-content {
    display: flex;
    flex: 1 0 auto;
    flex-direction: column;
    &__body {
      font-size: 20px;
      margin: 0rem 1rem;
    }
    &__heading {
      display: flex;
      align-items: center;
      &-title {
        font-weight: bold;
        font-size: 20px;
        margin: 0rem 1rem;
      }
      &-type {
        background-color: whitesmoke;
        color: gray;
        font-size: 15px;
        margin: 0rem 1rem;
      }
      &-time {
        @include muted-font();
        margin: 0rem 1rem;
      }
    }
  }
}
</style>
