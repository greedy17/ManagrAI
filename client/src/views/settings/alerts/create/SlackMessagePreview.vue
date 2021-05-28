<template>
  <div class="slack-message">
    <div class="slack-message__container">
      <div class="slack-message__container-icon">
        <!-- vertical icon -->
      </div>
      <div class="slack-message__container-content">
        <!-- horizontal stacked divs -->
        <div class="slack-message__container-content__heading">
          <!--Horizontal spans -->
          <span class="slack-message__container-content__heading-title">
            Managr
          </span>
          <span class="slack-message__container-content__heading-type">
            APP
          </span>
          <span class="slack-message__container-content__heading-time">
            {{ new Date() | timeOnlyShort }}
          </span>
        </div>
        <div class="slack-message__container-content__body">
          <div class="divider"></div>
          <span v-html="alert.message" style="word-wrap:break-word;"></span>
          <div class="divider"></div>
          <button class="btn btn--primary">Update {{ alert.resourceType }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SlackMessagePreview',
  props: {
    alert: { type: Object, default: () => {} },
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
@import '@/styles/mixins/buttons';
.btn {
  &--primary {
    @include primary-button();
  }
}

.slack-message {
  box-shadow: 0.2rem 0.5rem 0.5rem 0.2rem whitesmoke, -0.2rem 0.5rem 0.5rem 0.2rem whitesmoke;

  padding: 0.8rem 2rem;
  border-radius: 1rem;
  min-height: 10rem;
  width: 100%;
}
.slack-message__container {
  display: flex;
  &-icon {
    background-image: url(../../../../assets/images/logo.png);
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
      font-size: 16px;
      margin: 0rem 1rem;
      width: 25rem;
    }
    &__heading {
      display: flex;
      align-items: center;
      &-title {
        font-weight: bold;
        font-size: 20px;
        margin: 0rem 1rem;
        max-width: 35rem;
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
  .divider {
    @include standard-border();
    margin: 1rem 0rem;
  }
}
</style>
