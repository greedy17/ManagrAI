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
          <span class="slack-notif__container-content__heading-title"> Managr </span>
          <span class="slack-notif__container-content__heading-type"> APP </span>
          <span class="slack-notif__container-content__heading-time">
            {{ timeOnlyShort }}
          </span>
        </div>
        <div class="slack-notif__container-content__body">
          <p v-html="msg"></p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import moment from 'moment/src/moment'
export default {
  name: 'SlackNotificationTemplate',
  props: {
    msg: String,
    active: {
      type: Boolean,
      default: true,
    },
  },
  computed: {
    timeOnlyShort() {
      let date = new Date()
      return moment(date).format('HH:MM a')
    },
  },
}
</script>

<style scoped lang="scss">
@import '@/styles/variables';
@import '@/styles/mixins/utils';
.slack-notif {
  // box-shadow: 1px 1px 1px 2px whitesmoke, -1px 1px 1px whitesmoke;
  border: 1px solid $soft-gray;
  height: 5rem;
  padding: 0.75rem;
  border-radius: 8px;
  width: 40vw;
  min-height: 30vh;
}
.slack-notif__container {
  display: flex;
  &-icon {
    background-image: url(../../../../assets/images/logo.png);
    background-repeat: no-repeat;
    background-size: contain;
    background-position: center;
    height: 24px;
    width: 40px;
  }
  &-content {
    display: flex;
    flex: 1 0 auto;
    flex-direction: column;
    &__body {
      font-size: 14px;
      margin: 1rem 0.5rem;
      width: 30vw;
      height: 20vh;
      padding: 8px;
      overflow: scroll;
    }
    &__heading {
      display: flex;
      align-items: center;
      &-title {
        font-weight: bold;
        font-size: 20px;
        margin-top: -4px;
        margin: 0rem 1rem;
      }
      &-type {
        background-color: whitesmoke;
        color: gray;
        font-size: 15px;
        margin: 0rem 1rem;
        padding: 4px;
        border-radius: 4px;
      }
      &-time {
        @include muted-font();
        margin: 0rem 1rem;
      }
    }
  }
}
</style>
