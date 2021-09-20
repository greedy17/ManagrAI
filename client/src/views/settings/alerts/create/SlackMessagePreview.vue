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
          <span class="slack-message__container-content__heading-title"> Managr </span>
          <span class="slack-message__container-content__heading-type"> APP </span>
          <span class="slack-message__container-content__heading-time">
            {{ new Date() | timeOnlyShort }}
          </span>
        </div>
        <div class="slack-message__container-content__body">
          <span class="row__preview" style="word-wrap: break-word">
            <p>
              Hey {{ userName }}, your deal with Netflix has a passed closed date . Please update
              it!
            </p>
            <div class="column__buttons">
              <button class="update">Update Opportunity</button>
              <button class="playbook">Open Playbook</button>
              <button class="recording">Call recording</button>
            </div>
          </span>
          <div class="divider"></div>
          <em style="align-self: flex-start; color: #beb5cc">
            This Opportunity is owned by {{ userName }}
            <span style="margin-left: 2rem; color: white">Example</span>
          </em>
        </div>
        <!-- <p style="align-self: flex-end; color: #beb5cc">Example</p> -->
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
  data() {
    return {
      userName: this.$store.state.user.firstName + ' ' + this.$store.state.user.lastName,
    }
  },
}
</script>

<style scoped lang="scss">
@import '@/styles/variables';
@import '@/styles/mixins/utils';
@import '@/styles/mixins/buttons';

.update {
  color: white;
  background-color: teal;
  border: none;
  font-weight: bold;
  width: 9rem;
  height: 2rem;
  border-radius: 0.25rem;
  margin-bottom: 0.25rem;
}
.playbook {
  color: white;
  background-color: tomato;
  border: none;
  font-weight: bold;
  width: 9rem;
  height: 2rem;
  border-radius: 0.25rem;
  margin-bottom: 0.25rem;
}
.recording {
  color: white;
  background-color: transparent;
  border: 1px solid white;
  font-weight: bold;
  width: 9rem;
  height: 2rem;
  border-radius: 0.25rem;
}
.column__buttons {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.row__preview {
  display: flex;
  flex-direction: row;
}
.slack-message {
  box-shadow: 1px 2px 4px black;
  background-color: $panther;
  padding: 0.8rem 2rem;
  border-radius: 1rem;
  min-height: 12rem;
  width: 40vw;
}
.slack-message__container {
  display: flex;
  color: white;
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
        color: $panther-silver;
      }
      &-type {
        background-color: whitesmoke;
        color: gray;
        font-size: 13px;
        font-weight: bold;
        margin: 0rem 1rem;
        padding: 0.2rem;
        border-radius: 0.25rem;
      }
      &-time {
        @include muted-font();
        margin: 0rem 1rem;
      }
    }
  }
  .divider {
    // @include standard-border();
    margin: 1rem 0rem;
  }
}
</style>
